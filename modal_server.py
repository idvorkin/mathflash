#!python3
from icecream import ic
from modal import Image, App, forward, Function, Dict, asgi_app
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
import datetime
import requests
import main
import os
import time


# setup modal app state
image = Image.debian_slim().pip_install(["hyperdiv", "icecream", "requests"])
app = App("mathflash")  # Note: prior to April 2024, "app" was called "stub"
app.image = image
state = Dict.from_name(f"{app.name}-default-dict", create_if_missing=True)


class KEY:
    server_url = "server_url"
    innvocation_count = "innvocation_count"


# https://modal.com/docs/guide/webhooks
web_app = FastAPI()


@app.function(image=image)
@asgi_app()
def fastapi_app():
    return web_app


@app.function()
@web_app.get("/{full_path:path}")
async def get_redirect_to_server(request: Request, full_path: str):
    server_url = state.get(KEY.server_url, None)
    is_up = is_website_up(server_url)
    if not is_up:
        start_server_and_wait_for_it_to_be_up()
    return RedirectResponse(f"{server_url}/{full_path}", status_code=303)


@app.function(concurrency_limit=1, timeout=300)
def serve_on_modal():
    ic("called at", datetime.datetime.now())
    port = 8887  # tell hyperdiv to bind to a port (doesn't matter which)
    os.environ["HD_HOST"] = "0.0.0.0"
    os.environ["HD_PORT"] = str(port)
    with forward(port) as tunnel:
        state[KEY.server_url] = tunnel.url  # type:ignore # tunnel.url is the public URL of the server
        state[KEY.innvocation_count] = state.get(KEY.innvocation_count, 0) + 1  # type:ignore
        # this call is blocking, so this never returns
        # Run the hyperdiv app
        main.run()


def start_server_and_wait_for_it_to_be_up():
    print("Server is not running, starting it now ...")
    server_url = state[KEY.server_url] = ""  # type:ignore
    Function.lookup(app.name, "serve_on_modal").spawn()  # type: ignore
    # now busy wait for the server to start
    while True:
        print("Waiting for server to start ...")
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
