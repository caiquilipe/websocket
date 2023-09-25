from fastapi import FastAPI
from repositories.player_repository import PlayerInRedisRepository
from routes.websocket_endpoint import WebsocketRoute
from broadcaster import Broadcast
import logging

logging.basicConfig(
    level=logging.WARNING, format="%(asctime)s - %(levelname)s - %(message)s"
)


broadcast = Broadcast("redis://redis")
player_repository = PlayerInRedisRepository("redis://redis-session")


class Application(FastAPI):
    def __init__(
        self, broadcast: "Broadcast", player_repository: "PlayerInRedisRepository"
    ):
        self.__broadcast = broadcast
        self.__player_repository = player_repository
        super().__init__(
            on_startup=[self.__broadcast.connect, self.__player_repository.connect],
            on_shutdown=[
                self.__broadcast.disconnect,
                self.__player_repository.disconnect,
            ],
        )
        self._add_route()

    def _add_route(self):
        self.include_router(WebsocketRoute(self.__broadcast, self.__player_repository))


app = Application(broadcast)
