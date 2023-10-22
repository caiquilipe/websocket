from fastapi import FastAPI
from consume import consume, connect, disconnect


class Application(FastAPI):
    def __init__(self):
        super().__init__(
            on_startup=[consume, connect],
            on_shutdown=[
                disconnect,
            ],
        )


app = Application()
