from pathlib import Path
from typing import Annotated

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from typer import Option, Typer

from cli_arena.registry.client import RegistryClient
from cli_arena.registry.manager import upsert_dataset
from zipfile import ZipFile, ZIP_DEFLATED
import subprocess
import json

datasets_app = Typer(no_args_is_help=True)
console = Console()


@datasets_app.command()
def list(
    name: Annotated[
        str | None,
        Option(
            "--name",
            "-n",
            help=(
                "Name of the dataset. If provided, only list datasets with this name."
            ),
        ),
    ] = None,
    registry_url: Annotated[
        str,
        Option(
            help="Registry URL (should be an endpoint that returns text-based json).",
        ),
    ] = RegistryClient.DEFAULT_REGISTRY_URL,
    local_registry_path: Annotated[
        Path | None,
        Option(
            help=(
                "Path to a local registry json file. If provided, will use the local "
                "registry instead of the remote registry."
            ),
        ),
    ] = None,
):
    """List all datasets in the registry."""
    client = RegistryClient(
        registry_url=registry_url,
        local_registry_path=local_registry_path,
    )

    datasets = client.get_datasets()

    if name is not None:
        datasets = [d for d in datasets if d.name == name]

    table = Table(show_header=True, header_style="bold", show_lines=True)
    table.add_column("Name")
    table.add_column("Version")
    table.add_column("Description")
    table.add_column("ArenaBench Version")
    table.add_column("Compatible?")

    for d in sorted(datasets, key=lambda x: (x.name, x.version), reverse=True):
        is_compatible = d.is_compatible_with(client._current_version)
        table.add_row(
            d.name,
            d.version,
            d.description or "",
            d.terminal_bench_version,
            "✓" if is_compatible else "✗",
        )

    console.print(table)


@datasets_app.command()
def publish(
    repo_dir: Annotated[Path, Option("--repo", help="Repository directory containing tasks/")],
    name: Annotated[str, Option("--name", help="Dataset name")],
    version: Annotated[str, Option("--version", help="Dataset version, e.g. 0.1.0")],
    github_url: Annotated[str, Option("--github-url", help="GitHub URL of source repo")],
    branch: Annotated[str, Option("--branch", help="Branch name for source state")],
    commit_hash: Annotated[str, Option("--commit", help="Commit hash for source state")],
    dataset_path: Annotated[str, Option("--dataset-path", help="Relative path to tasks root", show_default=True)] = "tasks",
    description: Annotated[str | None, Option("--description", help="Optional description")] = None,
    out_dir: Annotated[Path, Option("--out", help="Output directory", show_default=True)] = Path("outputs/registry"),
    local_registry: Annotated[Path | None, Option("--local-registry", help="Path to local registry.json to update")]=None,
):
    """Create distributable artifacts (registry row JSON and zip bundle) for a dataset."""
    out_dir.mkdir(parents=True, exist_ok=True)
    tasks_path = repo_dir / dataset_path
    if not tasks_path.exists():
        console.print(f"[red]tasks path not found:[/red] {tasks_path}")
        raise typer.Exit(code=1)

    # Create zip bundle
    zip_path = out_dir / f"{name}_{version}.zip"
    with ZipFile(zip_path, "w", ZIP_DEFLATED) as zf:
        for p in tasks_path.rglob("*"):
            if p.is_file():
                zf.write(p, p.relative_to(repo_dir))

    # Create registry row JSON
    row = {
        "name": name,
        "version": version,
        "description": description,
        "terminal_bench_version": "latest",
        "github_url": github_url,
        "dataset_path": dataset_path,
        "branch": branch,
        "commit_hash": commit_hash,
        "task_id_subset": None,
    }
    meta_path = out_dir / f"{name}_{version}.json"
    meta_path.write_text(json.dumps(row, indent=2))

    console.print(f"[green]Wrote[/green] {zip_path}")
    console.print(f"[green]Wrote[/green] {meta_path}")
    # Optionally upsert into a local registry.json to mirror TB’s approach
    if local_registry is not None:
        added = upsert_dataset(local_registry, meta_path)
        action = "updated" if added == 0 else "added"
        console.print(f"[green]{action}[/green] entry in {local_registry}")


