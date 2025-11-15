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
                "user_input": "Всё очень ахуенно",
                "chat_id": "72ec218-a4e9-4221-82ef-05eef1416bfb"
            }
        ) as response:

            print("🔄 Отправка запроса...\n")
            try:
                data = await response.json()
            except aiohttp.ContentTypeError:
                # Если сервер вернул не JSON
                text = await response.text()
                print("Ответ текст:", text)
                return

            # Выводим весь ответ в формате, похожем на стриминг
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