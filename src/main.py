from fastapi import FastAPI
from repositories.player_repository import PlayerInRedisRepository
from routes.websocket_endpoint import WebsocketRoute
from repositories.bus_repository import BusRepository
from broadcaster import Broadcast
import logging
import json
import asyncio
import time


logging.basicConfig(
    level=logging.WARNING, format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


broadcast = Broadcast("redis://redis")
player_repository = PlayerInRedisRepository("redis://redis-session")
bus_repository = BusRepository("amqp://guest:guest@rabbitmq/")

async def callback(body: bytes):
    payload = json.loads(body)
    logger.warning(f" [x] EVENT - {int(time.time() - payload['timestamp'])} seconds")
    payload["timestamp"] = time.time()
    await broadcast.publish(payload["websocket_id"], json.dumps(payload))

    
async def many_consumer():
    consumer_tasks = [bus_repository.consume(callback, "websocket") for i in range(50)]
    await asyncio.gather(*consumer_tasks)
    
async def consumer():
    asyncio.create_task(many_consumer())
    
class Application(FastAPI):
    def __init__(
        self,
        broadcast: "Broadcast",
        player_repository: "PlayerInRedisRepository",
        bus_repository: "BusRepository",
    ):
        self.__broadcast = broadcast
        self.__player_repository = player_repository
        self.__bus_repository = bus_repository
        super().__init__(
            on_startup=[
                self.__broadcast.connect,
                self.__player_repository.connect,
                self.__bus_repository.connect,
                consumer,
            ],
            on_shutdown=[
                self.__broadcast.disconnect,
                self.__player_repository.disconnect,
                self.__bus_repository.disconnect,
            ],
        )
        self._add_route()

    def _add_route(self):
        self.include_router(
            WebsocketRoute(
                self.__broadcast, self.__player_repository, self.__bus_repository
            )
        )


app = Application(broadcast, player_repository, bus_repository)
