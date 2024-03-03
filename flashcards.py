#!python3

import utils
import hyperdiv as hd
import random
import time
from icecream import ic


router = hd.router()

operator_to_english = {
    "+": "Adding",
    "-": "Subtracting",
    "*": "Multiplying",
    "/": "Dividing",
}


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
    state.header = f"""# Let's practice {operator_to_english[state.operator]}
### Progress {state.questions_complete}/{state.total_question} {correct_string}
### [ {state.remaining_time} of {state.total_time} seconds left ]



"""
    state.header += extra



@router.route("/")
def home():
    hd.markdown("Try /operator/max_number")
    hd.markdown("e.g. [/-/20](http://site/-/20)")

def one_second_tick(state):
    time.sleep(1)
    ic("one_second_tick", state.remaining_time)
    if not state.start_dialog_done: # todo make a state machine
        return

    if state.remaining_time > 0:
        state.remaining_time -=1


def make_number_pad(state):
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


def DrawStartDialogOnFirstRun(state):
    if not state.start_dialog_done:
        dialog = hd.dialog(f"Welcome! Lets practice {operator_to_english[state.operator]}")
        with dialog:
            hd.text(f"Let's do {state.total_question} questions")
            b = hd.button("Start")
            if b.clicked:
                state.start_dialog_done = True
            dialog.opened = True

def DrawDoneDialogWhenDone(state):
    if state.remaining_time == 0:
        dialog = hd.dialog("My Dialog")
        with dialog:
            hd.text("Congrats you're all done!")
            hd.text(f"You got {state.correct_answers} correct!")
        dialog.opened = True


@router.route("/{operator}/{max}")
def operator_page(operator, max):
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
        total_time=30,
        remaining_time=30,
        start_dialog_done=False,
    )
    # start the loop
    onesecondtask = hd.task()
    onesecondtask.run(one_second_tick, state)
    if not onesecondtask.running:
        onesecondtask.rerun(one_second_tick, state)

    DrawStartDialogOnFirstRun(state)
    DrawDoneDialogWhenDone(state)

    if state.current_question == "":
        make_math_question(state)
        make_header(state)

    hd.markdown(state.header)


    make_header(state)


    with hd.hbox(
        padding=1,
        gap=1,
        border="1px solid yellow",
    ):
        hd.button(state.current_question)
        hd.button("=")
        hd.text_input(value=state.user_input, placeholder="answer")

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
                if int(state.user_input) == utils.safe_eval(state.current_question.strip()):
                    state.correct_answers += 1
                make_math_question(state)
            state.user_input = ""

    make_number_pad(state)

def main():
    router.run()


hd.run(main)

