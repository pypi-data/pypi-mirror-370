import os
from typing import *

import click
import preparse

__all__ = ["file_generator", "file_list", "main"]


def file_generator(*paths: Any) -> Generator[str, None, None]:
    "This generator yields the files under the given path."
    for raw_path in paths:
        path = str(raw_path)
        path = os.path.expanduser(path)
        path = os.path.expandvars(path)
        if os.path.isfile(path):
            yield path
            continue
        for root, dnames, fnames in os.walk(path):
            for fname in fnames:
                file = os.path.join(root, fname)
                yield file


def file_list(*paths: Any) -> List[str]:
    "This function returns a list of the files under the given path."
    return list(file_generator(*paths))


@preparse.PreParser().click()
@click.command(add_help_option=False)
@click.help_option("-h", "--help")
@click.version_option(None, "-V", "--version")
@click.argument("path", nargs=-1)
def main(path: Iterable) -> None:
    "This command lists files under given paths."
    for f in file_list(*path):
        click.echo(f)


if __name__ == "__main__":
    main()
