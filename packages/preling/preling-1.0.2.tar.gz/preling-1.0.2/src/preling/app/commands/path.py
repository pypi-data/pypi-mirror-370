from typing import Annotated

from typer import Argument

from preling.app.app import app
from preling.db import get_path
from preling.utils.typer import typer_raise

__all__ = [
    'path',
]


@app.command()
def path(
        language: Annotated[
            str,
            Argument(help='Language code whose data file should be printed.'),
        ],
) -> None:
    """Print the absolute path to PreLing’s data file for `language`."""
    language_path = get_path(language)
    if language_path.exists():
        print(language_path.absolute())
    else:
        typer_raise(f'Language "{language}" is not initialized.')
