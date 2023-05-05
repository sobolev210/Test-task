import json
import asyncio
from datetime import datetime

import aiofiles
from fastapi import FastAPI
from pydantic import BaseModel

from background_services import control_manipulator


class SensorData(BaseModel):
    datetime: datetime
    payload: int


app = FastAPI()
bg_task = asyncio.create_task(control_manipulator())


@app.post("/sensor-data/")
async def sensor_data(data: SensorData):
    async with aiofiles.open("sensor-data.json", "a") as f:
        await f.write(f"{json.dumps(data.dict(), default=str)}\n")
    return "OK"
