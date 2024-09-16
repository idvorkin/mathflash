#!python3
from icecream import ic
from modal import Image, App, forward, Function, Dict, asgi_app
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import datetime
import requests
from flashcards import LogQuestionAttempt
import main
import os
import time
import random
import socket

# setup modal app state
image = Image.debian_slim().pip_install(
    ["hyperdiv", "icecream", "requests", "pydantic>2.7", "fastapi>0.110"]
)
app = App("mathflash")  # Note: prior to April 2024, "app" was called "stub"
app.image = image
state = Dict.from_name(f"{app.name}-default-dict", create_if_missing=True)
question_attempts = Dict.from_name(
    f"{app.name}-question_attemps-dict", create_if_missing=True
)


class KEY:
    server_url = "server_url"
    innvocation_count = "innvocation_count"


# https://modal.com/docs/guide/webhooks
web_app = FastAPI()


@app.function()
@asgi_app()
def fastapi_app():
    return web_app


@app.function()
@web_app.post("/persist_attempt")
async def persist_attempt(attempt: LogQuestionAttempt):
    # for now just write to a modal dict
    key = random.randint(0, 2_000_000_000)
    attempt_as_dict = {
        "time": attempt.current_time,
        "user": attempt.user,
        "a": attempt.a,
        "b": attempt.b,
        "operation": attempt.operation,
        "right_answer": attempt.right_answer,
        "user_answer": attempt.user_answer,
        "correct": attempt.correct,
        "duration": attempt.duration_in_milliseconds,
        "other": attempt.other,
    }
    question_attempts[key] = attempt_as_dict  # type:ignore


@app.function()
@web_app.get("/attempts")
async def get_question_attempts():
    # for now just write to a modal dict
    # create a csv from question_attempts
    csv = "time,user,a,b,operation,right_answer,user_answer,correct,duration,other\n"

    # sort items by time before returning
    items = list(question_attempts.items())
    items.sort(key=lambda x: x[1]["time"])
    for _, attempt in items:
        csv += f"{attempt['time']},{attempt['user']},{attempt['a']},{attempt['b']},{attempt['operation']},{attempt['right_answer']},{attempt['user_answer']},{attempt['correct']},{attempt['duration']},{attempt['other']}\n"
    return HTMLResponse(csv)


class Config:
    REFRESH_TIMEOUT = 1  # seconds


@app.function()
@web_app.get("/{full_path:path}")
async def get_redirect_to_mathflash(request: Request, full_path: str):
    server_url = state.get(KEY.server_url, None)
    is_up = is_website_up(server_url)
    if not is_up:
        start_server_and_wait_for_it_to_be_up()

    url = f"{server_url}/{full_path}"
    html_page = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Math Flash</title>
<style>
  body, html {{
    margin: 0;
    padding: 0;
    height: 100%;
  }}
  iframe {{
    display: block;
    width: 100%;
    height: 100%;
    border: none;
  }}
  #loading {{
    display: none;
    text-align: center;
    padding-top: 50px;
  }}
</style>
<script>
  function checkIframeLoaded() {{
    var iframe = document.getElementById('mathFlashFrame');
    var loadingMessage = document.getElementById('loading');
    
    if (iframe.contentDocument.body.innerHTML.trim() === '') {{
      loadingMessage.style.display = 'block';
      setTimeout(function() {{
        window.location.reload(1);
      }}, {Config.REFRESH_TIMEOUT * 1000});
    }}
  }}
</script>
</head>
<body>
<iframe id="mathFlashFrame" src="{url}" onload="checkIframeLoaded()"></iframe>
<div id="loading">
  <h1>Server not up yet... refreshing</h1>
</div>
</body>
</html>
    """
    return HTMLResponse(html_page)


@app.function(concurrency_limit=1, timeout=300)
def run_mathflash_on_modal():
    ic("called at", datetime.datetime.now())
    port = 8887  # tell hyperdiv to bind to a port (doesn't matter which)

    def is_port_in_use(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(("0.0.0.0", port)) == 0

    for p in range(port, port + 1000):
        if not is_port_in_use(p):
            port = p
            break

    ic("Using Port", port)
    os.environ["HD_HOST"] = "0.0.0.0"
    with forward(port) as tunnel:
        state[KEY.server_url] = tunnel.url  # type:ignore # tunnel.url is the public URL of the server
        state[KEY.innvocation_count] = state.get(KEY.innvocation_count, 0) + 1  # type:ignore
        # this call is blocking, so this never returns
        # Run the hyperdiv app
        main.run(port=port)


def start_server_and_wait_for_it_to_be_up():
    print("Server is not running, starting it now ...")
    state[KEY.server_url] = ""  # type:ignore - clear cached server as we're creating a new one
    mathflash_server = Function.lookup(app.name, "run_mathflash_on_modal")  # type:ignore
    ic(mathflash_server)
    ret = mathflash_server.spawn()  # type: ignore
    ic(ret)
    # now busy wait for the server to start
    i = 0
    while True:
        i += 1
        print(f"Waiting for server to start [{i}]...")
        server_url = state.get(KEY.server_url, None)
        is_up = is_website_up(server_url)
        if is_up:
            break
        time.sleep(1)


def is_website_up(url):
    try:
        response = requests.get(url, timeout=0.5)
        # If the response status code is 200, the website is considered up
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        # If there is any exception (like a connection error), the website is considered down
        print(f"Error checking website: {e}")
        return False
