#!python3
import hyperdiv as hd
import homepage as hp
import typer
import flashcards as fc
# from icecream import ic

cli_app = typer.Typer()
router = hd.router()

def main():
    router.run()

@router.route("/")
def homepage():
    hp.home()


@router.route("/{operator}/{max}")
def operator_page(operator, max):
    fc.operator_page(operator, max)


@cli_app.command()
def run():
    hd.run(main)

if __name__ == "__main__":
    cli_app()
