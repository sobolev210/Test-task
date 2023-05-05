import asyncio
import time
from random import randint
from datetime import datetime

from aiohttp import ClientSession
from pydantic import BaseSettings


class Settings(BaseSettings):
    controller_url: str
    rps: int


async def send_data(controller_url: str, data: dict, session: ClientSession):
    try:
        await session.post(controller_url, json=data)
    except Exception as e:
        print(f"Error in sending data to Controller. Message: {e}")


async def start_sensor_data_generation_loop(settings: Settings):

    interval = 1/settings.rps
    start = time.time()

    async with ClientSession() as session:
        count = 0
        metrics_sent = False

        while True:
            payload = randint(0, 101)
            data = {"datetime": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), "payload": payload}
            asyncio.create_task(
                send_data(
                    controller_url=settings.controller_url,
                    data=data,
                    session=session
                ))

            await asyncio.sleep(interval)

            # The rest part - to make results presentable
            count += 1

            if not metrics_sent and time.time() - start >= 10:
                print("Time passed:", time.time() - start)
                print("Number of requests: ", count)
                metrics_sent = True


if __name__ == "__main__":
    settings = Settings()
    asyncio.run(start_sensor_data_generation_loop(settings))
