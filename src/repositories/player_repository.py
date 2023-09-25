import redis


class PlayerInRedisRepository:
    def __init__(self, url_connection: str) -> None:
        self.__url_connection = url_connection
        self.__pool = None

    def connect(self):
        connection_pool = redis.ConnectionPool.from_url(self.__url_connection)
        self.__pool = redis.Redis(connection_pool=connection_pool)

    def disconnect(self):
        self.__pool.close()

    def add_session(self, session_id: str, token: str):
        self.__pool.set(session_id, token)

    def remove_session(self, session_id: str):
        self.__pool.delete(session_id)
