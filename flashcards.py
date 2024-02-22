import hyperdiv as hd
import random
import ast

router = hd.router()


# Thank you stack overflow
def safe_eval(s):
    whitelist = (
        ast.Expression,
        ast.Call,
        ast.Name,
        ast.Load,
        ast.BinOp,
        ast.UnaryOp,
        ast.operator,
        ast.unaryop,
        ast.cmpop,
        ast.Num,
    )
    tree = ast.parse(s, mode="eval")
    safe_dict = {}
    valid = all(isinstance(node, whitelist) for node in ast.walk(tree))
    if valid:
        result = eval(
            compile(tree, filename="", mode="eval"), {"__builtins__": None}, safe_dict
        )
        return result
    return 0


def make_math_question(state):
    n1 = random.randint(0, state.max)
    n2 = random.randint(0, state.max)
    # swap n1 and n2 if n2 is bigger than n1
    if n2 > n1:
        n1, n2 = n2, n1
    state.current_question = f"  {n1} {state.operator} {n2}"

    extra = ""
    if state.questions_complete >= state.total_question:
        extra = "\n# Congrats you are done!"
    make_header(state, extra)


def make_header(state, extra=""):
    correct_string = (
        f"- {state.correct_answers} correct" if state.correct_answers > 0 else ""
    )
    state.header = f"""# Math Flashcards For {state.operator}
### Progress {state.questions_complete}/{state.total_question} {correct_string} """
    state.header += extra


@router.route("/")
def home():
    hd.markdown("Try /operator/max_number")
    hd.markdown("e.g. [/-/20](http://site/-/20)")


@router.route("/{operator}/{max}")
def operator(operator, max):
    # Todo validate operator
    if operator not in ["+", "-", "*", "/"]:
        hd.markdown("Invalid operator: {operator}")
        return

    state = hd.state(
        user_input="",
        questions=[],
        total_question=3,
        questions_complete=0,
        max=int(max),
        operator=operator,
        current_question="",
        header="",
        correct_answers=0,
    )
    if state.current_question == "":
        make_math_question(state)
        make_header(state)

    hd.markdown(state.header)
    with hd.hbox(
        padding=1,
        gap=1,
        border="1px solid yellow",
    ):
        hd.button(state.current_question)
        hd.button("=")
    with hd.hbox(
        padding=1,
        gap=1,
        border="1px solid yellow",
    ):
        if hd.button("back").clicked:
            state.user_input = state.user_input[:-1]
        if hd.button("clear").clicked:
            state.user_input = ""
        if hd.button("submit").clicked:
            # evaluate the answer
            # if it matches, print success
            # if can't convert to int, just clear it
            if state.user_input.isdigit():
                state.questions_complete += 1
                if int(state.user_input) == safe_eval(state.current_question.strip()):
                    state.correct_answers += 1
                make_math_question(state)
            state.user_input = ""

    def make_button(n):
        b1 = hd.button(n)
        if b1.clicked:
            state.user_input += n

    with hd.hbox(
        padding=1,
        gap=1,
        border="1px solid yellow",
    ):
        make_button("1")
        make_button("2")
        make_button("3")
        make_button("4")
        make_button("5")
    with hd.hbox(
        padding=1,
        gap=1,
        border="1px solid yellow",
    ):
        make_button("6")
        make_button("7")
        make_button("8")
        make_button("9")
        make_button("0")


def main():
    router.run()


hd.run(main)
