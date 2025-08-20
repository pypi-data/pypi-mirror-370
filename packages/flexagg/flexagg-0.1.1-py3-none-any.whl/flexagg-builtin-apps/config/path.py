from pathlib import Path

from typer import Typer, Argument
from typing_extensions import Annotated

from flexagg.config import config
from flexagg.utils import echo

app = Typer()


@app.command(name="ls")
def list_path():
    """
    List all paths in the flexagg cli path.
    """
    for path in config.all_dirs:
        echo.print(path.absolute())


@app.command(name="add")
def add_path(
    path: Annotated[
        Path,
        Argument(help="Path to add to the flexagg cli path"),
    ],
):
    """
    Add a path to the flexagg cli path.
    """
    config.add_dir(path)
    config.save()
    echo.success(f"{path.absolute()} Added.")


@app.command(name="del")
def del_path(
    path: Annotated[
        Path,
        Argument(help="Path to remove from the flexagg cli path"),
    ],
):
    """
    Remove a path from the flexagg cli path.
    """
    if config.remove_dir(path):
        config.save()
        echo.success(f"{path.absolute()} Deleted.")
