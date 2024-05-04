#!python3

# pylint: disable=missing-function-docstring
import os
import hyperdiv as hd
import typer

import flashcards as fc
import homepage as hp

# from icecream import ic

cli_app = typer.Typer()
router = hd.router()


def main():
    # template gives us a nice header and side bar.
    # Too early, and messes up pagination
    # template = hd.template(title="Math Flash")
    # with template.body:
    router.run()


@router.route("/")
def homepage():
    hp.home()


@router.route("/{operator}/{max}")
def operator_page(operator, max):
    fc.operator_page(operator, max)


@cli_app.command()
def run(port=8999):
    indexpage = hd.index_page(title="Math Flash", description="Get Great at Math")
    os.environ["HD_PORT"] = str(port)
    hd.run(main, index_page=indexpage)


if __name__ == "__main__":
    cli_app()
