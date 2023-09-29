from repository import BusRepository
import logging
import json
import time
import asyncio

logger = logging.getLogger(__name__)

bus_repository = BusRepository("amqp://guest:guest@rabbitmq/")


async def callback(body):
    payload = json.loads(body)
    logger.warning(f" [x] COMMAND - {int(time.time() - payload['timestamp'])} seconds")
    payload["timestamp"] = time.time()
    body = json.dumps(payload).encode("utf-8")
    await bus_repository.publish(body, "websocket")

async def consume():
    asyncio.create_task(many_consumer())
        
async def connect():
    await bus_repository.connect()
    
async def disconnect():
    await bus_repository.disconnect()
    
async def many_consumer():
    consumer_tasks = [bus_repository.consume(callback, "bus") for i in range(50)]
    await asyncio.gather(*consumer_tasks)