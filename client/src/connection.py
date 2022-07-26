#!/usr/bin/env python

import json
import uuid
from typing import Callable, List, Union

uid = uuid.uuid1().int >> 64


async def authenticate(websocket):
    await websocket.send(json.dumps({"authenticate": uid}))
    response = await websocket.recv()
    if json.loads(response) == {"authenticate": True}:
        print("Authenticated")
    else:
        print("Failed to authenticate")


async def searching(websocket, call_when_done: Callable):
    await websocket.send(json.dumps({"id": uid, "searching": True}))
    response = await websocket.recv()
    match = json.loads(response).get("matches")
    if isinstance(match, int):
        print("Match found")
        call_when_done(match)


async def update_data(
    websocket,
    data: List[Union[int, int, bool, str, bool]],
    call_when_done: Callable,
    call_when_game_over: Callable = lambda: 0,
):  # data is in the form (position x, position y, is_dead, animation_state, is_done)
    await websocket.send(json.dumps({"id": uid, "data": data}))
    response = await websocket.recv()
    positions = json.loads(response).get("data")
    if isinstance(positions, list):
        *positions, is_done = positions
        if is_done:
            call_when_game_over()
        call_when_done(positions)


async def leave(websocket, call_when_done: Callable):
    await websocket.send(json.dumps({"id": uid, "leave": True}))
    response = await websocket.recv()
    done = json.loads(response).get("left")
    if isinstance(done, bool) and done:
        call_when_done()
