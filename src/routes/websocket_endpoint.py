from fastapi import APIRouter, WebSocket
from repositories.websocket_repository import WebsocketRepository

from typing import TYPE_CHECKING
import logging


if TYPE_CHECKING:
    from broadcaster import Broadcast
    from repositories.bus_repository import BusRepository

logger = logging.getLogger(__name__)


class WebsocketRoute(APIRouter):
    def __init__(
        self,
        broadcast: "Broadcast",
        bus_repository: "BusRepository",
    ):
        super().__init__()

        self.__broadcast = broadcast
        self.__bus_repository = bus_repository
        self._add_route()

    def _add_route(self):
        self.add_websocket_route("/ws/", self.websocket_endpoint)

    async def websocket_endpoint(self, websocket: "WebSocket"):
        websocket_repository = WebsocketRepository(
            websocket, self.__broadcast, self.__bus_repository
        )
        try:
            await websocket_repository.connect()
            await websocket_repository.disconnect()
        except Exception as e:
            logger.error(f"Error: {e}")
            raise e
