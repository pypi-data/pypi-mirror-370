from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.table import Table
from rich.console import Console

from cli_arena.leaderboard.leaderboard import Leaderboard
from cli_arena.leaderboard.web import build_web
from cli_arena.leaderboard.enhanced_web import build_enhanced_web
from cli_arena.leaderboard.badges import generate_badges
from cli_arena.leaderboard.ci_integration import CIPipeline

leaderboard_app = typer.Typer(no_args_is_help=True)
console = Console()


@leaderboard_app.command()
def update(
    results: Annotated[Path, typer.Option("--results", help="Path to results JSON from harness")],
    db: Annotated[Path, typer.Option("--db", help="Leaderboard DB path", show_default=True)] = Path("outputs/leaderboard.json"),
    min_ts: Annotated[Optional[str], typer.Option("--min-ts", help="Minimum ISO timestamp; ignore older results")] = None,
):
    lb = Leaderboard(db)
    added = lb.update_from_results(results, min_ts=min_ts)
    console.print(f"Added {added} rows to leaderboard: {db}")


@leaderboard_app.command()
def show(
    db: Annotated[Path, typer.Option("--db", help="Leaderboard DB path", show_default=True)] = Path("outputs/leaderboard.json"),
    markdown: Annotated[bool, typer.Option("--md", help="Output markdown to stdout")] = False,
):
    lb = Leaderboard(db)
    if markdown:
        console.print(lb.to_markdown())
        return

    # Overall
    rows = lb.standings()
    overall = Table(title="Overall (All Repos/Tasks)")
    overall.add_column("Agent")
    overall.add_column("Evaluations", justify="right")
    overall.add_column("Verify Pass", justify="right")
    overall.add_column("Verify Rate", justify="right")
    overall.add_column("Agent OK", justify="right")
    overall.add_column("Agent Rate", justify="right")
    overall.add_column("Avg Time (s)", justify="right")
    overall.add_column("Trials Verify %", justify="right")
    overall.add_column("Avg Rubric", justify="right")
    for r in rows:
        overall.add_row(
            r["agent"],
            str(r["evaluations"]),
            str(r["verify_pass"]),
            f"{r['verify_rate']:.1f}%",
            str(r["agent_ok"]),
            f"{r['agent_rate']:.1f}%",
            f"{r['avg_time_s']:.2f}",
            (f"{r['avg_trials_verify_rate']:.1f}%" if r.get('avg_trials_verify_rate') is not None else "-"),
            (f"{r['avg_rubric_total']:.3f}" if r.get('avg_rubric_total') is not None else "-"),
        )
    console.print(overall)

    # Per repo
    by_repo = lb.standings_by_repo()
    for repo, table_rows in sorted(by_repo.items()):
        t = Table(title=f"Repo: {repo}")
        t.add_column("Agent")
        t.add_column("Evaluations", justify="right")
        t.add_column("Verify Pass", justify="right")
        t.add_column("Verify Rate", justify="right")
        t.add_column("Agent OK", justify="right")
        t.add_column("Agent Rate", justify="right")
        t.add_column("Avg Time (s)", justify="right")
        for r in table_rows:
            t.add_row(
                r["agent"],
                str(r["evaluations"]),
                str(r["verify_pass"]),
                f"{r['verify_rate']:.1f}%",
                str(r["agent_ok"]),
                f"{r['agent_rate']:.1f}%",
                f"{r['avg_time_s']:.2f}",
            )
        console.print(t)

    # Per task
    by_task = lb.standings_by_task()
    for repo, tasks in sorted(by_task.items()):
        for task, table_rows in sorted(tasks.items()):
            t = Table(title=f"Task: {repo}/{task}")
            t.add_column("Agent")
            t.add_column("Evaluations", justify="right")
            t.add_column("Verify Pass", justify="right")
            t.add_column("Verify Rate", justify="right")
            t.add_column("Agent OK", justify="right")
            t.add_column("Agent Rate", justify="right")
            t.add_column("Avg Time (s)", justify="right")
            for r in table_rows:
                t.add_row(
                    r["agent"],
                    str(r["evaluations"]),
                    str(r["verify_pass"]),
                    f"{r['verify_rate']:.1f}%",
                    str(r["agent_ok"]),
                    f"{r['agent_rate']:.1f}%",
                    f"{r['avg_time_s']:.2f}",
                )
            console.print(t)


@leaderboard_app.command()
def web(
    db: Annotated[Path, typer.Option("--db", help="Leaderboard DB path", show_default=True)] = Path("outputs/leaderboard.json"),
    out: Annotated[Path, typer.Option("--out", help="Output directory", show_default=True)] = Path("outputs/web"),
    enhanced: Annotated[bool, typer.Option("--enhanced", help="Build enhanced web interface with charts and real-time updates")] = False,
):
    if enhanced:
        idx = build_enhanced_web(out, db, enable_server=True)
        console.print(f"Built enhanced web leaderboard → {idx}")
        console.print("TIP: To start the real-time server, run: [bold]python -m cli_arena.leaderboard.server[/bold]")
    else:
        idx = build_web(out, db)
        console.print(f"Built web leaderboard → {idx}")


@leaderboard_app.command()
def badges(
    db: Annotated[Path, typer.Option("--db", help="Leaderboard DB path", show_default=True)] = Path("outputs/leaderboard.json"),
    out: Annotated[Path, typer.Option("--out", help="Output directory", show_default=True)] = Path("outputs/badges"),
):
    outputs = generate_badges(db, out)
    console.print(f"Wrote {len(outputs)} badge JSON files → {out}")


@leaderboard_app.command()
def serve(
    db: Annotated[Path, typer.Option("--db", help="Leaderboard DB path", show_default=True)] = Path("outputs/leaderboard.json"),
    host: Annotated[str, typer.Option("--host", help="Host to bind to")] = "0.0.0.0",
    port: Annotated[int, typer.Option("--port", help="Port to bind to")] = 8000,
    badge_dir: Annotated[Path, typer.Option("--badge-dir", help="Badge directory", show_default=True)] = Path("outputs/badges"),
):
    """Start the enhanced leaderboard server with real-time API."""
    try:
        from cli_arena.leaderboard.server import run_server
        console.print(f"LAUNCHING: Starting CLI Arena Leaderboard Server at http://{host}:{port}")
        console.print("📊 Enhanced web interface with real-time updates and API")
        run_server(host=host, port=port, db_path=db, badge_dir=badge_dir)
    except ImportError:
        console.print("[red]Error:[/red] FastAPI not installed. Install with: [bold]pip install fastapi uvicorn[/bold]")
    except Exception as e:
        console.print(f"[red]Error starting server:[/red] {e}")


@leaderboard_app.command()
def ci_setup(
    output_dir: Annotated[Path, typer.Option("--out", help="Output directory for CI files", show_default=True)] = Path("."),
):
    """Generate CI/CD pipeline configurations for automated leaderboard updates."""
    pipeline = CIPipeline()
    
    # Create GitHub Actions workflow
    gh_workflow_path = output_dir / ".github" / "workflows" / "leaderboard.yml"
    pipeline.create_github_actions_workflow(gh_workflow_path)
    console.print(f"SUCCESS: Created GitHub Actions workflow: {gh_workflow_path}")
    
    # Create GitLab CI config  
    gitlab_ci_path = output_dir / ".gitlab-ci.yml"
    pipeline.create_gitlab_ci_config(gitlab_ci_path)
    console.print(f"SUCCESS: Created GitLab CI config: {gitlab_ci_path}")
    
    console.print("\n[bold green]LAUNCHING: CI/CD Setup Complete![/bold green]")
    console.print("\nNext steps:")
    console.print("1. Commit the generated workflow files")
    console.print("2. Set up GitHub Pages or GitLab Pages for your repository")
    console.print("3. Configure any required secrets (API keys, etc.)")
    console.print("4. Run your first evaluation to populate the leaderboard")


@leaderboard_app.command()
def ci_update(
    max_files: Annotated[int, typer.Option("--max-files", help="Maximum number of recent result files to process")] = 10,
):
    """Update leaderboard from recent result files (for CI/CD usage)."""
    pipeline = CIPipeline()
    
    console.print("📊 Updating leaderboard from recent results...")
    total_added, processed_files = pipeline.update_from_recent_results(max_files)
    
    console.print(f"SUCCESS: Processed {len(processed_files)} files, added {total_added} rows")
    
    # Generate all artifacts
    console.print("🎨 Generating web artifacts...")
    artifacts = pipeline.generate_all_artifacts()
    
    console.print(f"SUCCESS: Generated {len(artifacts)} artifact types:")
    for artifact_type, path in artifacts.items():
        console.print(f"  - {artifact_type}: {path}")


@leaderboard_app.command() 
def deploy_summary():
    """Generate deployment summary for CI/CD pipelines."""
    pipeline = CIPipeline()
    summary = pipeline.create_deployment_summary()
    
    summary_path = Path("outputs/deployment_summary.json")
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    
    import json
    summary_path.write_text(json.dumps(summary, indent=2))
    
    console.print(f"📋 Created deployment summary: {summary_path}")
    
    if "error" not in summary:
        console.print(f"\n[bold green]📊 Deployment Stats:[/bold green]")
        console.print(f"  - Total Agents: {summary.get('total_agents', 0)}")
        console.print(f"  - Total Repositories: {summary.get('total_repositories', 0)}")
        if summary.get('top_agent'):
            console.print(f"  - Top Agent: {summary['top_agent']} ({summary.get('top_success_rate', 0):.1f}%)")

