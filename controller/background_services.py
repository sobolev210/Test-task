import os
import json
import asyncio
import socket
from datetime import datetime

import aiofiles


def send_control_signal(message: dict, sock: socket.socket):
    b_message = json.dumps(message).encode('utf-8')
    try:
        sock.sendall(b_message)
    except Exception as e:
        print(f"Error in sending data through socket. Reason: {e}")


async def control_manipulator():
    host = "manipulator"
    port = 65432

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
    except Exception:
        raise RuntimeError("Could not connect to Manipulator.")

    background_control_signal_tasks = set()
    while True:
        task = asyncio.create_task(generate_control_signal(sock))
        background_control_signal_tasks.add(task)
        task.add_done_callback(background_control_signal_tasks.discard)
        await asyncio.sleep(5)


async def generate_control_signal(sock: socket.socket):
    start = datetime.now()
    if not os.path.exists("sensor-data.json"):
        print("Sensor data is not ready yet.")
        return

    async with aiofiles.open("sensor-data.json", "r") as f:
        lines_count = 0
        payload_sum = 0

        async for line in f:
            try:
                data = json.loads(line.rstrip("\n"))
            except:
                pass
            timedelta = (start - datetime.strptime(data.get("datetime"), "%Y-%m-%d %H:%M:%S")).total_seconds()
            if timedelta < 0:  # data for the next control signal
                break
            elif not timedelta > 5:
                lines_count += 1
                payload_sum += data.get("payload")

        status = "down"
        if lines_count != 0:
            payload_average = payload_sum/lines_count
            if payload_average > 50:
                status = "up"
            print(f"Average payload: {round(payload_average, 2)}. Number of messages analysed: {lines_count}.")

        signal = {"datetime": start.strftime("%Y-%m-%dT%H:%M:%S"), "status": status}
        print(signal)
        send_control_signal(signal, sock)
