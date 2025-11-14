import asyncio
import os
import sys
import time

import aiohttp
import requests
import json
from dotenv import load_dotenv

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
load_dotenv()

from config import Config

API_URL = "https://yearly-flexible-canvasback.cloudpub.ru"
API_KEY = Config.API_KEY


async def test_query(question: str):
    data = {
        "question": question,
        "top_k": 3
    }
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }

    start_time = time.time()

    async with aiohttp.ClientSession() as session:
        tasks = [
            session.post(f"{API_URL}/query", json=data, headers=headers)
            for _ in range(1)
        ]
        # tasks = [
        #     session.get(f"{API_URL}/health")
        #     for _ in range(2)
        # ]

        responses = await asyncio.gather(*tasks)

        for i, response in enumerate(responses):
            print(f"Запрос {i + 1}: статус {response.status}")

    total_time = time.time() - start_time
    print(f"Общее время: {total_time:.2f} секунд")

    # Если время ~ равно времени одного запроса - работает параллельно
    # Если время = время_одного_запроса * количество - последователь


if __name__ == "__main__":
    asyncio.run(test_query("Какие есть правила вежливости в дирекции?"))