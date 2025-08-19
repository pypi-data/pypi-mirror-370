import os
from typing import *

import click
import preparse

__all__ = ["expandpath", "main"]


def expandpath(value: Any, /) -> Any:
    "This function expands a given path."
    ans: Any
    ans = os.path.expanduser(value)
    ans = os.path.expandvars(ans)
    return ans


@preparse.PreParser().click()
@click.command(add_help_option=False)
@click.help_option("-h", "--help")
@click.version_option(None, "-V", "--version")
@click.argument("path", type=str)
def main(path: str) -> None:
    "This command expands the given path."
    click.echo(expandpath(path))
