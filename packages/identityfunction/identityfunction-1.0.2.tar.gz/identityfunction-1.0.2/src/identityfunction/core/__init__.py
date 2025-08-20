from typing import *

import click
import preparse

__all__ = ["identityfunction", "main"]


def identityfunction(value: Any, /) -> Any:
    "This function returns the value given to it."
    return value


@preparse.PreParser().click()
@click.command(add_help_option=False)
@click.help_option("-h", "--help")
@click.version_option(None, "-V", "--version")
@click.argument("value", type=str)
def main(value: str) -> None:
    "This command applies the identity function to value."
    click.echo(identityfunction(value))
