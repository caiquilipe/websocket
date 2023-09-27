from typing import TYPE_CHECKING
import anyio
import logging
import json

if TYPE_CHECKING:
    from fastapi import WebSocket
    from broadcaster import Broadcast
    from anyio.abc import TaskGroup
    from repositories.bus_repository import BusRepository

logger = logging.getLogger(__name__)


class WebsocketRepository:
    def __init__(
        self,
        websocket: "WebSocket",
        broadcast: "Broadcast",
        bus_repository: "BusRepository",
    ):
        self.__broadcast = broadcast
        self.__websocket = websocket
        self.__bus_repository = bus_repository
        self.websocket_id = str(id(websocket))

    async def connect(self):
        await self.__websocket.accept()
        # TODO - Autenticar com a banca
        async with anyio.create_task_group() as task_group:
            task_group.start_soon(self.__receive_command, task_group)
            await self.__receive_event()

    async def disconnect(self):
        try:
            await self.__websocket.close()
        except:
            pass

    def __decode_command(self, message: bytes):
        try:
            return message[0], json.dumps(
                json.loads(message[1:].decode()) | {"websocket_id": self.websocket_id}
            )
        except Exception as e:
            logger.error(f"Error decoding message: {e}")
            raise KeyError

    async def __receive_command(self, task_group: "TaskGroup"):
        try:
            async for message in self.__websocket.iter_bytes():
                command, payload = self.__decode_command(message)
                self.__bus_repository.publish(payload, "bus")
        except KeyError:
            logger.error(f"{self.websocket_id} DISCONNECTED - Command received invalid")
        finally:
            logger.warning(f"{self.websocket_id} DISCONNECTED - Closing connection")
            task_group.cancel_scope.cancel()

    async def __receive_event(self):
        async with self.__broadcast.subscribe(channel=self.websocket_id) as subscriber:
            async for event in subscriber:
                try:
                    await self.__websocket.send_bytes(str(event.message).encode())
                except Exception as e:
                    logger.error(f"Error sending message: {e}")
                    break
