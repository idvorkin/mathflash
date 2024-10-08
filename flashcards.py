#!python3

import requests
import threading
import utils
from utils import operator_to_english, english_to_operator
import hyperdiv as hd
from keyboard_plugin import keyboard_capture
import random
import time
from enum import Enum, auto
from datetime import datetime, timedelta
from icecream import ic

from pydantic import BaseModel, ConfigDict


class LogQuestionAttempt(BaseModel):
    user: str
    current_time: str
    user: str
    a: int
    b: int
    operation: str
    right_answer: int
    user_answer: int
    correct: bool
    duration_in_milliseconds: int  # milliseconds
    other: str


class FlashcardState(Enum):
    WelcomeDialog = auto()
    Answering = auto()
    FinishedDialog = auto()


class ToastState(Enum):
    Empty = auto()
    Correct = auto()
    TryAgain = auto()


# This is a fake class to represent the types of state.
# need to make sure anything you add to here gets added in state til hyperdiv does a nice bridge
class FCState(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    name: str
    questions: list[str]
    total_question: int
    questions_complete: int
    max: int
    operator: str
    n1: int
    n2: int
    time_user_started_question: datetime
    current_question: str
    header: str
    correct_answers: int
    total_time: int
    remaining_time: int
    start_dialog_done: bool
    game_state: FlashcardState
    toast_start: datetime
    toast: ToastState
    input_box: hd.text_input


def init_operator_state(operator, max) -> FCState:
    operator = english_to_operator.get(operator, operator)
    # hd.state is a singleton and only initalized on the first call to hd.state
    # on the webpage

    return hd.state(
        name="Mike",
        questions=[],
        total_question=10,
        questions_complete=0,
        max=int(max),
        operator=operator,
        n1=0,
        n2=0,
        time_user_started_question=datetime.now(),
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
    )  # type:ignore


def make_math_question(state):
    n1 = random.randint(0, state.max)
    n2 = random.randint(0, state.max)
    # swap n1 and n2 if n2 is bigger than n1
    if n2 > n1:
        n1, n2 = n2, n1
    state.current_question = f"  {n1} {state.operator} {n2}"
    state.n1, state.n2 = n1, n2
    state.time_user_started_question = datetime.now()

    extra = ""
    if state.questions_complete >= state.total_question:
        extra = "\n# Congrats you are done!"

    make_header(state, extra)


def persist_question_attempt(attempt: LogQuestionAttempt):
    # hard code for now
    server = "https://idvorkin--mathflash-fastapi-app.modal.run"  # prod
    # server = "https://idvorkin--mathflash-fastapi-app-dev.modal.run" # dev

    # post a request to the server

    start = time.time()
    ic(
        server,
        attempt.user_answer,
        attempt.duration_in_milliseconds,
        attempt.current_time,
    )
    # annoying modal can't run pydantic 2.0 not sure which package is in conflict.
    response = requests.post(
        f"{server}/persist_attempt", json=attempt.model_dump_json()
    )
    ic(server, (attempt.user_answer, response, time.time() - start))
    if response.status_code != 200:
        ic(response.status_code)
        ic(attempt.model_dump_json())
        ic(response.text)


def make_toasts(state):
    if state.toast == ToastState.Empty:
        return

    should_show_toast = (datetime.now() - state.toast_start) < timedelta(seconds=0.8)

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

    font_size = 1.1  # this isn't seeming to be honored, but close enough
    hd.alert(
        "Hooray - Correct!", font_size=font_size, variant="success", opened=show_correct
    )
    hd.alert(
        "Close - Try Again!",
        font_size=font_size,
        variant="warning",
        opened=show_tryagain,
    )


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
    state.header = f"""### Let's practice {operator_to_english[state.operator]}
Progress {state.questions_complete}/{state.total_question} {correct_string}

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
        padding=0.5,
        gap=1,
        justify="center",
    )


# Get inspired by the calculator example
# https://github.com/hyperdiv/hyperdiv-apps/blob/main/calculator/calculator/main.py


def pretty_button(label, background_color="blue", width=4, pill=False, circle=True):
    return hd.button(
        label,
        width=width,  # type:ignore
        height=width,
        circle=circle,
        pill=pill,
        font_size=1.5,
        label_style=hd.style(align="center", justify="center"),
        background_color=background_color,
        font_color="neutral-50",
    )


def make_number_pad(state):
    def make_button(n):
        if pretty_button(n).clicked:
            state.input_box.value += n

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
            state.input_box.value = ""

        make_button("0")

        if pretty_button("⌫", background_color="yellow").clicked:
            state.input_box.value = state.input_box.value[:-1]


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


def on_submit_answer(state: FCState):
    user_answer = str(state.input_box.value)
    valid_answer_attempt = user_answer.isdigit()
    if not valid_answer_attempt:
        # Just clear invalid user input
        state.input_box.value = ""
        return

    is_answer_correct = int(user_answer) == utils.safe_eval(
        state.current_question.strip()
    )

    state.questions_complete += 1
    state.toast_start = datetime.now()

    if is_answer_correct:
        state.correct_answers += 1
        state.toast = ToastState.Correct
    else:
        state.toast = ToastState.TryAgain

    def state_to_attempt(state):
        duration = datetime.now() - state.time_user_started_question
        current_time = str(datetime.now())
        return LogQuestionAttempt(
            current_time=current_time,
            user=state.name,
            a=state.n1,
            b=state.n2,
            operation=state.operator,
            right_answer=7,
            user_answer=int(state.input_box.value),
            correct=is_answer_correct,
            duration_in_milliseconds=int(duration.total_seconds() * 1_000),
            other="other-stuff-to-add",
        )

    attempt = state_to_attempt(state)
    # run the persist function in a separate thread
    threading.Thread(
        target=persist_question_attempt, kwargs={"attempt": attempt}
    ).start()

    # create a new question
    make_math_question(state)
    state.input_box.value = ""


def handle_keyboard(state, keyboard):
    if key := keyboard.pressed_event.lower():
        ic(key)
        # if key is a number, add it to the input box
        if key in [str(i) for i in range(10)]:
            state.input_box.value += key
        if key == "backspace":
            state.input_box.value = state.input_box.value[:-1]
        if key == "return" or key == "enter":
            on_submit_answer(state)


def operator_page(operator, max):
    if operator not in utils.english_to_operator.keys():
        hd.markdown(f"Invalid operator: {operator}")
        return

    keys_to_capture = [str(i) for i in range(10)] + ["backspace", "return", "enter"]
    keyboard = keyboard_capture(capture=keys_to_capture)
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
    with make_row():
        hd.markdown(f"## {state.current_question}")

    # Draw the control buttons
    with make_row():
        ti = hd.text_input(value="", placeholder="answer")
        state.input_box = ti
        if hd.button("GO", background_color="green", font_color="neutral-50").clicked:
            on_submit_answer(state)

    make_number_pad(state)
    make_toasts(state)
    handle_keyboard(state, keyboard)
