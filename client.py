import websockets
import asyncio
import multiprocessing
import time
import json

async def receive(websocket):
    while True:
        try:
            payload = json.loads(await websocket.recv()) 
            print(f"MESSAGE - {int(time.time() - payload['timestamp_init'])} seconds on system and {int(time.time() - payload['timestamp'])} seconds on redis message")
        except Exception:
            pass


async def hello():
    uri = "ws://127.0.0.1/ws"
    async with websockets.connect(uri) as websocket:
        print("Conectado ao servidor.")
        number = 1
        asyncio.get_event_loop().create_task(receive(websocket))
        while True:
            message = json.dumps({"teste": "teste", "timestamp_init": time.time()})
            await websocket.send(number.to_bytes(1, "big") + message.encode("utf-8"))
            await asyncio.sleep(10)

def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(*[hello() for _ in range(250)]))
    loop.close()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    for _ in range(10):
        multiprocessing.Process(target=main).start()
        time.sleep(1)
