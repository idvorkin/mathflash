#!python3
import typer
from icecream import ic
from modal import Image, App, forward, Function, Dict, asgi_app
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
import datetime
import requests
import main

web_app = FastAPI()


app = App("mathflash")  # Note: prior to April 2024, "app" was called "stub"
MODAL_IMAGE = Image.debian_slim().pip_install(["hyperdiv","icecream", "requests"])
app.image = MODAL_IMAGE

MATHFLASH_DICT = Dict.from_name(f"{app.name}-default-dict", create_if_missing=True)

# https://modal.com/docs/guide/webhooks
@app.function(image=MODAL_IMAGE)
@asgi_app()
def fastapi_app():
    return web_app


class KEY:
    server_url = "server_url"
    innvocation_count = "innvocation_count"

@app.function(concurrency_limit=1, timeout=300)
def serve_on_modal():
    import os
    ic("called at", datetime.datetime.now())

    # setenv of HD_HOST is not working
    port = 8887
    os.environ["HD_HOST"] = "0.0.0.0"
    os.environ["HD_PORT"] = str(port)
    with forward(port) as tunnel:
        MATHFLASH_DICT[KEY.server_url] = tunnel.url
        MATHFLASH_DICT[KEY.innvocation_count]  = MATHFLASH_DICT.get(KEY.innvocation_count, 0) + 1
        main.local_debug_server()

@app.function()
@web_app.get("/{full_path:path}")
async def read_all(request: Request, full_path: str):
    # check if the server is running ... if not, start it
    import time
    server_url = MATHFLASH_DICT.get(KEY.server_url, None)
    is_up = is_website_up(server_url)
    url_path = str(request.url)
    if (not is_up):
        print("Server is not running, starting it now ...")
        server_url = MATHFLASH_DICT[KEY.server_url] = ""
        f = Function.lookup(app.name, "serve_on_modal")
        f.spawn()
        # now busy wait for the server to start
        while True:
            print("Waiting for server to start ...")
            server_url = MATHFLASH_DICT.get(KEY.server_url, None)
            is_up = is_website_up(server_url)
            if is_up:
                break
            time.sleep(1)
    return RedirectResponse(f"{server_url}/{full_path}", status_code=303)


def is_website_up(url):
    try:
        response = requests.get(url)
        # If the response status code is 200, the website is considered up
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        # If there is any exception (like a connection error), the website is considered down
        print(f"Error checking website: {e}")
        return False

