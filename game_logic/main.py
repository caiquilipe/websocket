from repository import BusRepository
import logging

logger = logging.getLogger(__name__)

bus_repository = BusRepository("amqp://guest:guest@rabbitmq")
bus_repository.connect()


def callback(ch, method, properties, body):
    logger.warning(" [x] Received %r" % body)
    bus_repository.publish(body, "websocket")


def consume():
    bus_repository.consume(callback, "bus")


consume()
bus_repository.disconnect()
