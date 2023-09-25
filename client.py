import websockets
import asyncio
import multiprocessing


async def receive(websocket):
    while True:
        try:
            print(await websocket.recv())
        except Exception:
            pass


async def hello():
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        print("Conectado ao servidor.")
        number = 1
        asyncio.get_event_loop().create_task(receive(websocket))
        while True:
            await websocket.send(number.to_bytes(1, "big") + b"{'teste': 'teste'}")
            await asyncio.sleep(2)


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(*[hello() for _ in range(250)]))
    loop.close()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    for _ in range(1):
        multiprocessing.Process(target=main).start()
