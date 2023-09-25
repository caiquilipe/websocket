from fastapi import APIRouter, WebSocket
from repositories.websocket_repository import WebsocketRepository
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from broadcaster import Broadcast


class WebsocketRoute(APIRouter):
    def __init__(self, broadcast: "Broadcast"):
        super().__init__()
        self.__broadcast = broadcast
        self._add_route()

    def _add_route(self):
        self.add_websocket_route("/ws", self.websocket_endpoint)

    async def websocket_endpoint(self, websocket: "WebSocket"):
        websocket_repository = WebsocketRepository(websocket, self.__broadcast)
        await websocket_repository.connect()
        await websocket_repository.disconnect()
