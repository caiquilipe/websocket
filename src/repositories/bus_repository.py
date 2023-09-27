import pika
import logging

logger = logging.getLogger(__name__)


class BusRepository:
    def __init__(self, url_connection: str) -> None:
        self.__url_connection = url_connection

    def connect(self):
        self.__connection = pika.BlockingConnection(
            pika.ConnectionParameters(self.__url_connection)
        )
        self.__channel = self.__connection.channel()

    def publish(self, message, queue):
        self.__channel.basic_publish(exchange="", routing_key=queue, body=message)
        logger.warning(f" [x] Sent {message}")

    def consume(self, callback, queue):
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(self.__url_connection)
            )
            channel = connection.channel()
            channel.queue_declare(queue=queue)
            channel.basic_consume(
                queue=queue, on_message_callback=callback, auto_ack=True
            )
            logger.warning(" [*] Waiting for messages. To exit press CTRL+C")
            channel.start_consuming()
        finally:
            connection.close()

    def disconnect(self):
        self.__connection.close()
