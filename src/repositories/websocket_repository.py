from repositories.auth_repository import authenticate
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
        query_params = self.__websocket.query_params
        await authenticate(websocket_id=self.websocket_id, **query_params)
        await self.__websocket.accept()
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
            payload = {
                "websocket_id": self.websocket_id,
                "data": json.dumps(json.loads(message[1:]))
            }
            return self.__choices(message[0]), json.dumps(payload)
        except Exception as e:
            logger.error(f"Error decoding message: {e}")
            raise KeyError
    
    def __choices(self, command: int):
        choices = {
            2: "join_lobby",
            3: "start",
            4: "play",
            8: "play_auto",
            5: "cashout",
            6: "user_bets",
            7: "consult_auto"
        }
        return choices[command]

    async def __receive_command(self, task_group: "TaskGroup"):
        try:
            async for message in self.__websocket.iter_bytes():
                command, payload = self.__decode_command(message)
                await self.__bus_repository.publish(payload.encode("utf-8"), command)
        except KeyError:
            logger.error(f"{self.websocket_id} DISCONNECTED - Command received invalid")
        finally:
            logger.warning(f"{self.websocket_id} DISCONNECTED - Closing connection")
            task_group.cancel_scope.cancel()

    async def __receive_event(self):
        async with self.__broadcast.subscribe(channel=self.websocket_id) as subscriber:
            logger.warning(f"Subscribed to channel: {self.websocket_id}")
            async for event in subscriber:
                try:
                    payload = json.loads(event.message)
                    response = int_to_bytes(payload["event_id"]) + payload["data"].encode("utf-8")
                    await self.__websocket.send_bytes(response)
                except Exception as e:
                    logger.error(f"Error sending message: {e}")
                    break

def int_to_bytes(number: int):
    return number.to_bytes(1, byteorder="big")