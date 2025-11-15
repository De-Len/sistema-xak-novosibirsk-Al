import asyncio
import os
import sys
import aiohttp
from dotenv import load_dotenv

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
load_dotenv()

from config import Config

API_URL = "http://0.0.0.0:8000/query"
API_KEY = Config.API_KEY

async def test_full_response():
    """Тестирует обычный endpoint, выдающий полный ответ сразу"""
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            API_URL,
            headers=headers,
            json={
                "user_input": "Всё хорошо (тестовый ответ) давай дальше",
                "chat_id": "d2aa2f5f-919e-4605-a503-f3c00298f9b6"
            }
        ) as response:

            print("🔄 Отправка запроса...\n")
            try:
                data = await response.json()
            except aiohttp.ContentTypeError:
                text = await response.text()
                print("Ответ текст:", text)
                return

            content = data.get("content", "")
            print("📝 Ответ:")
            print(content)

            print(f"\n✅ Запрос завершён!")
            print(f"📊 Chat ID: {data.get('chat_id')}")
            print(f"❓ Прогресс: {data.get('question_count')}/{data.get('total_questions')}")
            print(f"🏁 Завершен: {data.get('is_completed')}")

# Запуск теста
if __name__ == "__main__":
    asyncio.run(test_full_response())