from multiprocessing import Array, Event, Process
from time import sleep, time
from ujson import loads as json_loads

import pytest

from sanic import Sanic
from sanic.response import json
from sanic.utils import local_request, HOST, PORT


# ------------------------------------------------------------ #
#  GET
# ------------------------------------------------------------ #

# TODO: Figure out why this freezes on pytest but not when
# executed via interpreter
@pytest.mark.skip(
    reason="Freezes with pytest not on interpreter")
def test_multiprocessing():
    app = Sanic('test_json')

    response = Array('c', 50)
    @app.route('/')
    async def handler(request):
        return json({"test": True})

    stop_event = Event()
    async def after_start(*args, **kwargs):
        http_response = await local_request('get', '/')
        response.value = http_response.text.encode()
        stop_event.set()

    def rescue_crew():
        sleep(5)
        stop_event.set()

    rescue_process = Process(target=rescue_crew)
    rescue_process.start()

    app.serve_multiple({
        'host': HOST,
        'port': PORT,
        'after_start': after_start,
        'request_handler': app.handle_request,
        'request_max_size': 100000,
    }, workers=2, stop_event=stop_event)

    rescue_process.terminate()

    try:
        results = json_loads(response.value)
    except:
        raise ValueError("Expected JSON response but got '{}'".format(response))

    assert results.get('test') == True

@pytest.mark.skip(
    reason="Freezes with pytest not on interpreter")
def test_drain_connections():
    app = Sanic('test_json')

    @app.route('/')
    async def handler(request):
        return json({"test": True})

    stop_event = Event()
    async def after_start(*args, **kwargs):
        http_response = await local_request('get', '/')
        stop_event.set()

    start = time()
    app.serve_multiple({
        'host': HOST,
        'port': PORT,
        'after_start': after_start,
        'request_handler': app.handle_request,
    }, workers=2, stop_event=stop_event)
    end = time()

    assert end - start < 0.05
