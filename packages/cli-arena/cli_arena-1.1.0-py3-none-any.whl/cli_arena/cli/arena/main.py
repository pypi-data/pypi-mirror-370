import dotenv
from typer import Typer

from .admin import admin_app
from .cache import cache_app
from .datasets import datasets_app
from .runs import create, runs_app
from .tasks import tasks_app
from .leaderboard import leaderboard_app
from .docker_cli import docker_app
from .registry_cli import app as registry_app
from .quality_cli import app as quality_app

dotenv.load_dotenv()

app = Typer(no_args_is_help=True)
app.add_typer(tasks_app, name="tasks", help="Manage tasks.")
app.add_typer(datasets_app, name="datasets", help="Manage datasets.")
app.add_typer(runs_app, name="runs", help="Manage runs.")
app.add_typer(cache_app, name="cache", help="Cache management commands.")
app.add_typer(admin_app, name="admin", help="Admin commands (private).", hidden=True)
app.add_typer(leaderboard_app, name="leaderboard", help="Leaderboard commands.")
app.add_typer(docker_app, name="docker", help="Docker utilities.")
app.add_typer(registry_app, name="registry", help="Dataset registry management.")
app.add_typer(quality_app, name="quality", help="Task quality management and validation.")

app.command(name="run", help="Run the CLI Arena harness (alias for `arena runs create`)")(create)

if __name__ == "__main__":
    app()


