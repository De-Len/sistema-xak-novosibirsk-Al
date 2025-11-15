import asyncio
import os
import ssl
import sys

import aiohttp
import json

from dotenv import load_dotenv

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
load_dotenv()

from config import Config

API_URL = "https://yearly-flexible-canvasback.cloudpub.ru/query-streaming"  # ← ДОБАВЛЕН ПУТЬ /query-streaming
API_KEY = Config.API_KEY

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE


async def test_streaming():
    """Тестирует streaming endpoint"""
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }

    connector = aiohttp.TCPConnector(ssl=ssl_context)

    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.post(
                API_URL,  # ← Теперь правильный URL
                headers=headers,
                json={
                    "user_input": "d445c5b7-b638-4008-a848-fc61c8652f17",
                    "chat_id": "Хорошо чувствую"
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