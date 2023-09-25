from typing import TYPE_CHECKING
import anyio
import logging

if TYPE_CHECKING:
    from fastapi import WebSocket
    from broadcaster import Broadcast
    from anyio.abc import TaskGroup

logger = logging.getLogger(__name__)


class WebsocketRepository:
    def __init__(self, websocket: "WebSocket", broadcast: "Broadcast"):
        self.__broadcast = broadcast
        self.__websocket = websocket
        self.__websocket_id = str(id(websocket))

    async def connect(self):
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
            return message[0], message[1:].decode()
        except Exception as e:
            logger.warning(f"Error decoding message: {e}")
            raise KeyError

    async def __receive_command(self, task_group: "TaskGroup"):
        try:
            async for message in self.__websocket.iter_bytes():
                command, payload = self.__decode_command(message)
                logger.warning(
                    f"Received command from {self.__websocket_id} - {command} - {payload}"
                )
                await self.__broadcast.publish(
                    channel=self.__websocket_id, message=payload
                )
        except KeyError:
            logger.warning(
                f"{self.__websocket_id} DISCONNECTED - Command received invalid"
            )
        finally:
            logger.warning(f"{self.__websocket_id} DISCONNECTED - Closing connection")
            task_group.cancel_scope.cancel()

    async def __receive_event(self):
        logger.warning(f"{self.__websocket_id} CONNECTED")
        async with self.__broadcast.subscribe(
            channel=self.__websocket_id
        ) as subscriber:
            logger.warning(f"{self.__websocket_id} SUBSCRIBED")
            async for event in subscriber:
                logger.warning(f"Sending event to 1: {self.__websocket_id}")
                try:
                    await self.__websocket.send_bytes(str(event.message).encode())
                except Exception as e:
                    logger.warning(f"Error sending message: {e}")
                    break
            logger.warning("No more events")
        logger.warning("No more subscribers")
