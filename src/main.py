from fastapi import FastAPI
from routes.websocket_endpoint import WebsocketRoute
from repositories.bus_repository import BusRepository
from broadcaster import Broadcast
from datadog import initialize, statsd
import logging
import json
import asyncio
import os

options = {
    "statsd_host": os.getenv("DATADOG_HOST"),
    "statsd_port": os.getenv("DATADOG_PORT"),
}

initialize(**options)

logging.basicConfig(
    level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


broadcast = Broadcast(os.getenv("WS_REDIS_URL"))
bus_repository = BusRepository(os.getenv("AIO_PIKA_HOST"))

def reset_metrics():
    statsd.gauge("websocket.connected", 0, tags=["environment:dev"])
    
async def callback(body: bytes):
    payload = json.loads(body)
    await broadcast.publish(payload["websocket_id"], json.dumps(payload))


async def consumer():
    asyncio.create_task(bus_repository.consume(callback, "personal_websocket"))

class Application(FastAPI):
    def __init__(
        self,
        broadcast: "Broadcast",
        bus_repository: "BusRepository",
    ):
        self.__broadcast = broadcast
        self.__bus_repository = bus_repository
        super().__init__(
            on_startup=[
                reset_metrics,
                self.__broadcast.connect,
                self.__bus_repository.connect,
                consumer,
            ],
            on_shutdown=[
                self.__broadcast.disconnect,
                self.__bus_repository.disconnect,
            ],
        )
        self._add_route()

    def _add_route(self):
        self.include_router(
            WebsocketRoute(
                self.__broadcast, self.__bus_repository
            )
        )


app = Application(broadcast, bus_repository)
