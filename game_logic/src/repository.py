import aio_pika
import logging
import asyncio


logger = logging.getLogger(__name__)


class BusRepository:
    def __init__(self, url_connection: str) -> None:
        self.__url_connection = url_connection

    async def connect(self):
        self.__connection = await aio_pika.connect_robust(self.__url_connection)
        self.__channel = await self.__connection.channel()

    async def publish(self, message, queue):
        await self.__channel.default_exchange.publish(
            aio_pika.Message(body=message), routing_key=queue
        )

    async def consume(self, callback, queue):
        connection = await aio_pika.connect_robust(self.__url_connection)
        try:
            async with connection.channel() as ch:
                queue = await ch.declare_queue(queue)

                async with queue.iterator() as queue_iter:
                    async for message in queue_iter:
                        async with message.process():
                            asyncio.get_event_loop().create_task(callback(message.body))
        finally:
            await connection.close()

    async def disconnect(self):
        await self.__connection.close()
