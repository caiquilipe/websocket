from fastapi import FastAPI
from routes.websocket_endpoint import WebsocketRoute
from broadcaster import Broadcast
import logging

logging.basicConfig(
    level=logging.WARNING, format="%(asctime)s - %(levelname)s - %(message)s"
)


broadcast = Broadcast("redis://redis")


class Application(FastAPI):
    def __init__(self, broadcast: "Broadcast"):
        self.__broadcast = broadcast
        super().__init__(
            on_startup=[self.__broadcast.connect],
            on_shutdown=[self.__broadcast.disconnect],
        )
        self._add_route()

    def _add_route(self):
        self.include_router(WebsocketRoute(self.__broadcast))


app = Application(broadcast)
