#!python3

import utils
from utils import operator_to_english, english_to_operator
import hyperdiv as hd
import random
import time
from enum import Enum, auto
from datetime import datetime, timedelta


class FlashcardState(Enum):
    WelcomeDialog = auto()
    Answering = auto()
    FinishedDialog = auto()


class ToastState(Enum):
    Empty = auto()
    Correct = auto()
    TryAgain = auto()


def init_operator_state(operator, max):
    operator = english_to_operator.get(operator, operator)
    # hd.state is a singleton and only initalized on the first call to hd.state
    # on the webpage

    return hd.state(
        name="Mike",
        user_input="",
        questions=[],
        total_question=10,
        questions_complete=0,
        max=int(max),
        operator=operator,
        current_question="",
        header="",
        correct_answers=0,
        total_time=120,
        remaining_time=120,
        start_dialog_done=False,
        game_state=FlashcardState.WelcomeDialog,
        toast_start=0.0,
        toast=ToastState.Empty,
        last_property=None,
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


def handle_toast(state):
    if state.toast == ToastState.Empty:
        return

    should_show_toast = (datetime.now() - state.toast_start) < timedelta(seconds=0.5)

    if not should_show_toast:
        state.toast = ToastState.Empty
        return

    show_correct = False
    show_tryagain = False
    # make toasts inve
    if state.toast == ToastState.Correct:
        show_correct = True
    if state.toast == ToastState.TryAgain:
        show_tryagain = True

    hd.alert("Correct!", variant="success", opened=show_correct)
    hd.alert("Close - Try Again!", variant="warning", opened=show_tryagain)


### [ {state.remaining_time} of {state.total_time} seconds left ]


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

"""
    state.header += extra
    return state.header


def on_every_second(state):
    time.sleep(1)
    if not state.game_state == FlashcardState.Answering:
        return

    if state.remaining_time > 0:
        state.remaining_time -= 1


def make_row():
    return hd.hbox(
        padding=1,
        gap=1,
        border="1px solid yellow",
        justify="center",
    )


# Get inspired by the calculator example
# https://github.com/hyperdiv/hyperdiv-apps/blob/main/calculator/calculator/main.py


def pretty_button(label, background_color="blue", width=5, pill=False, circle=True):
    return hd.button(
        label,
        width=width,  # type:ignore
        height=5,
        circle=circle,
        pill=pill,
        font_size=1.8,
        label_style=hd.style(align="center", justify="center"),
        background_color=background_color,
        font_color="neutral-50",
    )


def make_number_pad(state):
    def make_button(n):
        if pretty_button(n).clicked:
            state.user_input += n

    with make_row():
        make_button("1")
        make_button("2")
        make_button("3")
    with make_row():
        make_button("4")
        make_button("5")
        make_button("6")
    with make_row():
        make_button("7")
        make_button("8")
        make_button("9")
    with make_row():
        if pretty_button("✖", background_color="yellow").clicked:
            state.user_input = ""

        make_button("0")

        if pretty_button("⌫", background_color="yellow").clicked:
            state.user_input = state.user_input[:-1]


# We're going to try to complete {state.total_question} questions in {state.total_time} seconds.
def make_welcome_dialog(state):
    dialog = hd.dialog(f"Welcome {state.name}! ")
    with dialog:
        hd.markdown(
            f"""Lets practice {operator_to_english[state.operator]} together!
"""
        )
        if hd.button("Start", width="100%").clicked:
            state.game_state = FlashcardState.Answering
        dialog.opened = True


def make_finished_dialog(state):
    dialog = hd.dialog("Congrats you're all done!")
    with dialog:
        hd.text(f"You got {state.correct_answers} correct!")
    dialog.opened = True


def on_submit_answer(state):
    valid_answer_attempt = state.user_input.isdigit()
    if not valid_answer_attempt:
        # Just clear invalid user input
        state.user_input = ""
        return

    is_answer_correct = int(state.user_input) == utils.safe_eval(
        state.current_question.strip()
    )

    state.questions_complete += 1
    state.toast_start = datetime.now()

    if is_answer_correct:
        state.correct_answers += 1
        state.toast = ToastState.Correct
    else:
        state.toast = ToastState.TryAgain

    # create a new question
    make_math_question(state)
    state.user_input = ""


def operator_page(operator, max):
    if operator not in utils.english_to_operator.keys():
        hd.markdown(f"Invalid operator: {operator}")
        return

    state = init_operator_state(operator, max)
    hd.markdown(make_header(state))

    # start the game timer loop
    timer_task = hd.task()
    timer_task.run(on_every_second, state)
    if not timer_task.running:
        timer_task.rerun(on_every_second, state)

    if state.game_state == FlashcardState.WelcomeDialog:
        make_welcome_dialog(state)
    if state.game_state == FlashcardState.FinishedDialog:
        make_finished_dialog(state)

    # Draw the question
    handle_toast(state)
    with make_row():
        hd.markdown(f"## {state.current_question}")

    # Draw the control buttons
    with make_row():
        hd.text_input(value=state.user_input, placeholder="answer")
        if hd.button("✅", background_color="green").clicked:
            on_submit_answer(state)

    make_number_pad(state)
