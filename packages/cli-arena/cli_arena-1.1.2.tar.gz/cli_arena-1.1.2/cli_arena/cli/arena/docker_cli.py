import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
import typer

docker_app = typer.Typer(help="Docker utilities for CLI Arena")


def _run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, text=True, capture_output=True)


@docker_app.command("gc")
def docker_gc(
    keep: int = typer.Option(2, help="Keep the latest N agent images per repo/agent"),
    max_age_hours: int = typer.Option(168, help="Prune agent images older than this many hours"),
    dry_run: bool = typer.Option(False, help="Show what would be deleted without deleting"),
):
    """Garbage collect agent images while preserving the base image.

    Images are expected to be labeled:
    - cli-arena.role=agent-image
    - cli-arena.repo=<repo>
    - cli-arena.agent=<agent>
    """
    # Age prune first
    until = f"{max_age_hours}h"
    typer.echo(f"Pruning images older than {max_age_hours}h (agent images only)...")
    prune_cmd = [
        "docker", "image", "prune", "-af",
        "--filter", f"until={until}",
        "--filter", "label=cli-arena.role=agent-image",
        "--filter", "label!=cli-arena.preserve=true",
    ]
    if dry_run:
        prune_cmd.append("--dry-run")
    _run(prune_cmd)

    # Keep last N per (repo, agent)
    typer.echo(f"Keeping last {keep} images per (repo, agent), removing older ones...")
    ls = _run(["docker", "images", "--format", "{{.Repository}} {{.Tag}} {{.ID}} {{.CreatedAt}}"])
    lines = [l.strip() for l in ls.stdout.splitlines() if l.strip()]
    buckets: dict[tuple[str, str], list[tuple[str, str]]] = {}
    for line in lines:
        # Example repo: gemini-cli-arena-cli-arena-ml-fastapi-b:latest
        repo_tag, tag, img_id, created_at = line.split(" ", 3)
        repo = repo_tag
        # Parse embedded labels by inspecting image (slow-path, but explicit)
        inspect = _run(["docker", "image", "inspect", "--format", "{{ index .Config.Labels \"cli-arena.repo\" }} {{ index .Config.Labels \"cli-arena.agent\" }} {{ index .Config.Labels \"cli-arena.role\" }}", repo + ":" + tag])
        parts = inspect.stdout.strip().split()
        if len(parts) != 3:
            continue
        repo_label, agent_label, role = parts
        if role != "agent-image":
            continue
        key = (repo_label or "unknown", agent_label or "unknown")
        buckets.setdefault(key, []).append((repo + ":" + tag, created_at))

    # Sort by created desc and remove older beyond keep
    to_remove: list[str] = []
    for key, images in buckets.items():
        images_sorted = sorted(
            images,
            key=lambda x: x[1],
            reverse=True,
        )
        for repo_tag, _ in images_sorted[keep:]:
            to_remove.append(repo_tag)
    if not to_remove:
        typer.echo("Nothing to remove.")
        return
    typer.echo(f"Removing {len(to_remove)} images...")
    if dry_run:
        for it in to_remove:
            typer.echo(f"DRY-RUN docker rmi {it}")
        return
    _run(["docker", "rmi", "-f", *to_remove])


