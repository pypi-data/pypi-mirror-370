from typing import *

import click
import preparse

__all__ = ["dummyfunction", "main"]


def dummyfunction(*args: Any, **kwargs: Any) -> None:
    "This function does nothing."
    pass


@preparse.PreParser().click()
@click.command(add_help_option=False)
@click.help_option("-h", "--help")
@click.version_option(None, "-V", "--version")
@click.argument("args", nargs=-1, type=str)
def main(args: Iterable[str]) -> None:
    "This command does nothing."
    pass
