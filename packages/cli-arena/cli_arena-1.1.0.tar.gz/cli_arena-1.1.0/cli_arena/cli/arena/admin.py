from pathlib import Path
from typing import Annotated

import typer

admin_app = typer.Typer(no_args_is_help=True)

@admin_app.command()
def noop(config: Annotated[Path, typer.Option(help="placeholder")]):
    print("Admin placeholder; implement as needed.")


