import asyncio
import os
import sys

import aiohttp
import json

from dotenv import load_dotenv

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
load_dotenv()

from config import Config

API_URL = "http://0.0.0.0:8000/query-streaming"  # ← ДОБАВЛЕН ПУТЬ /query-streaming
API_KEY = Config.API_KEY

async def test_streaming():
    """Тестирует streaming endpoint"""
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
                API_URL,  # ← Теперь правильный URL
                headers=headers,
                json={
                    "user_input": "иногда",
                    "chat_id": "8c18a21d-5d03-4465-b1b2-e379e51d1ada"
                }
        ) as response:

            print("🔄 Начало streaming...\n")
            accumulated_text = ""

            async for line in response.content:
                line = line.decode('utf-8').strip()

                if line.startswith('data: '):
                    try:
                        data = json.loads(line[6:])

                        if data.get('content'):
                            accumulated_text += data['content']
                            print(data['content'], end='', flush=True)

                        if data.get('is_final_chunk'):
                            print(f"\n\n✅ Stream завершен!")
                            print(f"📊 Chat ID: {data.get('chat_id')}")
                            print(f"❓ Прогресс: {data.get('question_count')}/{data.get('total_questions')}")
                            print(f"🏁 Завершен: {data.get('is_completed')}")

                    except json.JSONDecodeError:
                        continue

# Запуск теста
if __name__ == "__main__":
    asyncio.run(test_streaming())