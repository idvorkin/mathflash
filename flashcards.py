#!python3

import utils
from utils import operator_to_english, english_to_operator
import hyperdiv as hd
import random
import time
from enum import Enum, auto


router = hd.router()


class FlashcardState(Enum):
    WelcomeDialog = auto()
    Answering = auto()
    FinishedDialog = auto()


def make_operator_state(operator, max):
    return hd.state(
        name="Igor_Load_from_DB",
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
        game_state=FlashcardState.WelcomeDialog,
    )


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
    if state.current_question == "":
        make_math_question(state)

    if state.remaining_time <= 0:
        state.game_state = FlashcardState.FinishedDialog

    if state.questions_complete >= state.total_question:
        state.game_state = FlashcardState.FinishedDialog

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
    hd.markdown(
        """

# Welcome to math flash!

### Future features
* Eventually we'll have per user login,
    * Which will load settings and record answers to DB

### For now

* You need to pass the URL yourself
    * [/subtract/20](/subtract/20)
    * [/add/7](/subtract/7)
 """
    )


def one_second_tick(state):
    time.sleep(1)
    if not state.game_state == FlashcardState.Answering:
        return

    if state.remaining_time > 0:
        state.remaining_time -= 1


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


def WelcomeDialog(state):
    dialog = hd.dialog(f"Welcome {state.name}! ")
    with dialog:
        hd.markdown(
            f"""Lets practice {operator_to_english[state.operator]} together!

We're going to try to complete {state.total_question} questions in {state.total_time} seconds.


"""
        )
        if hd.button("Start", width="100%").clicked:
            state.game_state = FlashcardState.Answering
        dialog.opened = True


def FinishedDialog(state):
    dialog = hd.dialog("Congrats you're all done!")
    with dialog:
        hd.text(f"You got {state.correct_answers} correct!")
    dialog.opened = True


@router.route("/{operator}/{max}")
def operator_page(operator, max):
    operator = english_to_operator.get(operator, operator)
    state = make_operator_state(operator, max)
    # Todo validate operator
    if operator not in ["+", "-", "*", "/"]:
        hd.markdown("Invalid operator: {operator}")
        return

    make_header(state)
    hd.markdown(state.header)

    # start the loop
    onesecondtask = hd.task()
    onesecondtask.run(one_second_tick, state)
    if not onesecondtask.running:
        onesecondtask.rerun(one_second_tick, state)

    if state.game_state == FlashcardState.WelcomeDialog:
        WelcomeDialog(state)
    if state.game_state == FlashcardState.FinishedDialog:
        FinishedDialog(state)

    # Draw the question
    with hd.hbox(
        padding=1,
        gap=1,
        border="1px solid yellow",
    ):
        hd.button(state.current_question)
        hd.button("=")
        hd.text_input(value=state.user_input, placeholder="answer")

    # Draw the control buttons
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
            if not state.user_input.isdigit():
                # if can't convert to int, just clear it
                state.user_input = ""
            else:
                # it's a valid digit
                # evaluate the answer
                state.questions_complete += 1
                is_answer_correct = int(state.user_input) == utils.safe_eval(
                    state.current_question.strip()
                )
                if is_answer_correct:
                    state.correct_answers += 1
                    make_math_question(state)
                state.user_input = ""

    make_number_pad(state)


def main():
    router.run()


hd.run(main)
