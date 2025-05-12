from fastapi import WebSocket, WebSocketDisconnect
from fastapi.encoders import jsonable_encoder
from typing import Set, Dict

subscriptions: Dict[int, Set[WebSocket]] = {}


async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await websocket.accept()
    if user_id not in subscriptions:
        subscriptions[user_id] = set()
    subscriptions[user_id].add(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        subscriptions[user_id].remove(websocket)


async def send_data_to_subscribers(user_id: int, data):
    if user_id in subscriptions:
        data = jsonable_encoder(data)

        for websocket in subscriptions[user_id]:
            await websocket.send_json(data)
