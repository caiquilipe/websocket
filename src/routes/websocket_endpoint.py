from fastapi import APIRouter, WebSocket
from repositories.websocket_repository import WebsocketRepository
from typing import TYPE_CHECKING
import secrets
import logging


if TYPE_CHECKING:
    from repositories.player_repository import PlayerInRedisRepository
    from broadcaster import Broadcast

logger = logging.getLogger(__name__)


class WebsocketRoute(APIRouter):
    def __init__(
        self, broadcast: "Broadcast", player_repository: "PlayerInRedisRepository"
    ):
        super().__init__()
        self.__broadcast = broadcast
        self.__player_repository = player_repository
        self._add_route()

    def _add_route(self):
        self.add_websocket_route("/ws", self.websocket_endpoint)

    async def websocket_endpoint(self, websocket: "WebSocket"):
        websocket_repository = WebsocketRepository(websocket, self.__broadcast)
        try:
            logger.warning(f"Enter session: {websocket_repository.websocket_id}")
            self.__player_repository.add_session(
                websocket_repository.websocket_id, secrets.token_hex(16)
            )
            logger.warning(
                f"Total sessions: {self.__player_repository.count_sessions()}"
            )
            await websocket_repository.connect()
            await websocket_repository.disconnect()
        except Exception as e:
            logger.error(f"Error: {e}")
        finally:
            self.__player_repository.remove_session(websocket_repository.websocket_id)
            logger.warning(
                f"Total sessions: {self.__player_repository.count_sessions()}"
            )
