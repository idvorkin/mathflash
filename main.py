#!python3
import hyperdiv as hd
import homepage as hp
import flashcards as fc

router = hd.router()


def main():
    router.run()


@router.route("/")
def homepage():
    hp.home()


@router.route("/{operator}/{max}")
def operator_page(operator, max):
    fc.operator_page(operator, max)


hd.run(main)
