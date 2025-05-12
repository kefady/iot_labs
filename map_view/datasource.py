import asyncio
import json
from datetime import datetime
import websockets
from kivy import Logger
from pydantic import BaseModel, field_validator
from config import STORE_HOST, STORE_PORT


# Pydantic models
class ProcessedAgentData(BaseModel):
    road_state: str
    user_id: int
    x: float
    y: float
    z: float
    latitude: float
    longitude: float
    timestamp: datetime

    @classmethod
    @field_validator("timestamp", mode="before")
    def check_timestamp(cls, value):
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(value)
        except (TypeError, ValueError):
            raise ValueError(
                "Invalid timestamp format. Expected ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)."
            )


class Datasource:
    def __init__(self, user_id: int):
        self.index = 0
        self.user_id = user_id
        self.connection_status = None
        self._new_points = []
        asyncio.ensure_future(self.connect_to_server())

    def get_new_points(self):
        Logger.debug(self._new_points)
        points = self._new_points
        self._new_points = []
        return points

    async def connect_to_server(self):
        uri = f"ws://{STORE_HOST}:{STORE_PORT}/ws/{self.user_id}"
        while True:
            try:
                Logger.debug(f"Connecting to {uri}")
                async with websockets.connect(uri) as websocket:
                    self.connection_status = "Connected"
                    Logger.info("WebSocket connected")
                    while True:
                        data = await websocket.recv()
                        self.handle_received_data(data)
            except websockets.ConnectionClosed:
                self.connection_status = "Disconnected"
                Logger.warning("WebSocket connection closed. Reconnecting...")
                await asyncio.sleep(5)
            except Exception as e:
                Logger.error(f"WebSocket error: {e}")
                await asyncio.sleep(5)

    def handle_received_data(self, data):
        Logger.debug(f"Received raw data: {data}")
        try:
            parsed_data = json.loads(data)
            processed_agent_data_list = sorted(
                [ProcessedAgentData(**item) for item in parsed_data],
                key=lambda v: v.timestamp
            )
            new_points = [
                (
                    item.latitude,
                    item.longitude,
                    item.road_state
                )
                for item in processed_agent_data_list
            ]
            self._new_points.extend(new_points)
        except Exception as e:
            Logger.error(f"Error while processing data: {e}")
