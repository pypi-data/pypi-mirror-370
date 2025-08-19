from pathlib import Path

import ch5mpy as ch
import rich
import typer

from hdfq.evaluation import eval as hdfq_eval
from hdfq.parser import parse


def run(filter: str, path: Path) -> None:
    tree, mode = parse(filter)

    with ch.options(error_mode="ignore"):
        try:
            h5_object = ch.H5Dict.read(path, mode=mode)

        except IsADirectoryError:
            rich.print(f"[bold red]{path} is not a file[/bold red]")
            raise typer.Exit(code=10)

        except OSError:
            rich.print(f"[bold red]{path} is not a valid hdf5 file[/bold red]")
            raise typer.Exit(code=11)

        hdfq_eval(tree, h5_object)
