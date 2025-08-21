import shutil
import subprocess
from pathlib import Path
from typing import Annotated

import typer
from rich import print as rich_print
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
)

from cli_arena.registry.client import RegistryClient

cache_app = typer.Typer(no_args_is_help=True)

DOCKER_IMAGE_NAME_PREFIXES = ["arena_", "cli-arena"]


def _format_bytes(bytes_value: int) -> str:
    value = float(bytes_value)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if value < 1024.0:
            return f"{value:.1f} {unit}"
        value /= 1024.0
    return f"{value:.1f} PB"


def _get_image_size(image_name: str) -> int:
    try:
        result = subprocess.run(
            f"docker images --format '{{{{.Size}}}}' {image_name}",
            shell=True,
            capture_output=True,
            text=True,
            check=True,
        )
        size_str = result.stdout.strip().upper()
        if not size_str:
            return 0
        if size_str.endswith("KB"):
            return int(float(size_str[:-2]) * 1024)
        if size_str.endswith("MB"):
            return int(float(size_str[:-2]) * 1024 * 1024)
        if size_str.endswith("GB"):
            return int(float(size_str[:-2]) * 1024 * 1024 * 1024)
        if size_str.endswith("TB"):
            return int(float(size_str[:-2]) * 1024 * 1024 * 1024 * 1024)
        if size_str.endswith("B"):
            return int(float(size_str[:-1]))
        return int(float(size_str))
    except (subprocess.CalledProcessError, ValueError):
        return 0


def _get_directory_size(path: Path) -> int:
    total_size = 0
    try:
        for file_path in path.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size
    except (OSError, PermissionError):
        pass
    return total_size


@cache_app.command()
def clean(
    force: Annotated[
        bool, typer.Option("--force", "-f", help="Force removal without confirmation")
    ] = False,
) -> None:
    """Remove Arena-related Docker images/networks and clear cache directory."""

    cache_dir = RegistryClient.CACHE_DIR
    cache_exists = cache_dir.exists()

    if not force:
        rich_print(
            "[yellow]This will remove all Docker images and networks starting with "
            f"{DOCKER_IMAGE_NAME_PREFIXES}.[/]"
        )
        if cache_exists:
            rich_print(
                f"[yellow]This will also remove the cache directory: {cache_dir}[/]"
            )
        if not typer.confirm("Are you sure you want to continue?"):
            rich_print("[yellow]Operation cancelled.[/]")
            return

    total_space_freed = 0
    cache_space_freed = 0
    if cache_exists:
        cache_space_freed = _get_directory_size(cache_dir)

    grep_pattern = "|".join(DOCKER_IMAGE_NAME_PREFIXES)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        transient=True,
    ) as progress:
        if cache_exists:
            cache_task = progress.add_task("Removing cache directory...", total=1)
            try:
                shutil.rmtree(cache_dir)
                progress.update(cache_task, advance=1)
                rich_print(f"[green]Removed cache directory: {cache_dir}[/]")
            except (OSError, PermissionError) as e:
                rich_print(f"[red]Failed to remove cache directory: {e}[/]")
                cache_space_freed = 0
                progress.update(cache_task, advance=1)

        try:
            result = subprocess.run(
                "docker images --format '{{.Repository}}:{{.Tag}}' | " f"grep -E '{grep_pattern}'",
                shell=True,
                capture_output=True,
                text=True,
                check=False,
            )
            if result.stdout.strip():
                images = result.stdout.strip().split("\n")
                image_task = progress.add_task("Removing Docker images...", total=len(images))
                for image in images:
                    if image.strip():
                        image_size = _get_image_size(image.strip())
                        total_space_freed += image_size
                        try:
                            subprocess.run(f"docker rmi -f {image.strip()}", shell=True, check=True, capture_output=True)
                        finally:
                            progress.update(image_task, advance=1)
                rich_print(f"[green]Removed {len(images)} arena Docker images[/]")
            else:
                rich_print("[yellow]No arena Docker images found[/]")
        except subprocess.CalledProcessError:
            rich_print("[yellow]No arena Docker images found[/]")

        try:
            result = subprocess.run(
                "docker network ls --format '{{.Name}}' | " f"grep -E '{grep_pattern}'",
                shell=True,
                capture_output=True,
                text=True,
                check=False,
            )
            if result.stdout.strip():
                networks = result.stdout.strip().split("\n")
                network_task = progress.add_task("Removing Docker networks...", total=len(networks))
                for network in networks:
                    if network.strip():
                        try:
                            subprocess.run(f"docker network rm {network.strip()}", shell=True, check=True, capture_output=True)
                        finally:
                            progress.update(network_task, advance=1)
                rich_print(f"[green]Removed {len(networks)} arena Docker networks[/]")
            else:
                rich_print("[yellow]No arena Docker networks found[/]")
        except subprocess.CalledProcessError:
            rich_print("[yellow]No arena Docker networks found[/]")

    total_space_freed += cache_space_freed
    if total_space_freed > 0:
        rich_print(
            f"[bold green]Cleanup completed![/] [green]Freed {_format_bytes(total_space_freed)} of storage space.[/]"
        )
    else:
        rich_print("[bold green]Cleanup completed![/]")


