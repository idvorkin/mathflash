#!python3
import hyperdiv as hd
import homepage as hp
import typer
import flashcards as fc
from icecream import ic
from modal import Image, App, forward, Function

cli_app = typer.Typer()


app = App("mathflash")  # Note: prior to April 2024, "app" was called "stub"
app.image = Image.debian_slim().pip_install("hyperdiv;icecream".split(";"))

router = hd.router()


def main():
    router.run()


@router.route("/")
def homepage():
    hp.home()


@router.route("/{operator}/{max}")
def operator_page(operator, max):
    fc.operator_page(operator, max)


@app.function()
def serve_on_modal():
    import os

    # setenv of HD_HOST is not working
    port = 8887
    os.environ["HD_HOST"] = "0.0.0.0"
    os.environ["HD_PORT"] = str(port)
    with forward(port) as tunnel:
        ic(tunnel)
        print(tunnel.url)
        hd.run(main)


@cli_app.command()
def get_modal_port():
    f = Function.lookup("math_flash", "serve_on_modal")
    f.remote()


@cli_app.command()
def local():
    hd.run(main)


if __name__ == "__main__":
    cli_app()
