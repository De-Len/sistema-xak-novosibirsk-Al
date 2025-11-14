# src/infrastructure/chat_storage/MongoDBChatStorage.py
from typing import Optional, Dict, List
import uuid
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from src.application.use_cases.QueryLLMUseCase import IChatStorage


class MongoDBChatStorage(IChatStorage):
    def __init__(self, connection_string: str, database_name: str = "burnout_survey"):
        self.client = AsyncIOMotorClient(connection_string)
        self.db = self.client[database_name]
        self.chats = self.db["chat_sessions"]

        self.system_prompt = """
    Ты профессиональный психолог, проводящий опрос по методике выгорания Маслач (MBI). 
    Твоя задача:
    
    1. Задай мне 8 вопросов о моем эмоциональном состоянии и профессиональном выгорании
    2. Задавай вопросы ПО ОДНОМУ - сначала задай вопрос, дождись моего ответа, потом следующий вопрос
    3. Вопросы должны быть развернутыми, побуждающими к рефлексии, а не как в тесте с вариантами ответов
    4. После получения всех 8 ответов - проанализируй их и дай развернутые результаты по трем шкалам:
       - Эмоциональное истощение
       - Деперсонализация  
       - Редукция профессиональных достижений
    5. Также дай персональные рекомендации
    
    Не торопись, веди диалог естественно и поддерживающе.
    """

    async def create_chat(self, max_questions: int) -> str:
        chat_id = str(uuid.uuid4())

        chat_session = {
            '_id': chat_id,
            'created_at': datetime.now(),
            'messages': [
                {
                    "role": "system",
                    "content": self.system_prompt,
                    "timestamp": datetime.now()
                }
            ],
            'question_count': 0,
            'max_questions': max_questions,
            'status': 'active'
        }

        await self.chats.insert_one(chat_session)
        return chat_id

    async def get_chat(self, chat_id: str) -> Optional[Dict]:
        chat = await self.chats.find_one({'_id': chat_id})
        return chat

    async def add_message(self, chat_id: str, role: str, content: str):
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now()
        }

        await self.chats.update_one(
            {'_id': chat_id, 'status': 'active'},
            {'$push': {'messages': message}}
        )

    async def increment_question_count(self, chat_id: str):
        chat = await self.get_chat(chat_id)
        if chat:
            new_count = chat['question_count'] + 1
            update_data = {'$set': {'question_count': new_count}}

            if new_count > chat['max_questions']:
                update_data['$set']['status'] = 'completed'
                await self._schedule_chat_deletion(chat_id)

            await self.chats.update_one(
                {'_id': chat_id},
                update_data
            )

    async def is_chat_completed(self, chat_id: str) -> bool:
        chat = await self.get_chat(chat_id)
        return chat and chat.get('status') == 'completed'

    async def get_chat_messages(self, chat_id: str) -> List[Dict]:
        """Возвращает сообщения в формате для OpenAI API (без timestamp)"""
        chat = await self.get_chat(chat_id)
        if not chat:
            return []

        # Преобразуем сообщения в формат для OpenAI API
        openai_messages = []
        for msg in chat['messages']:
            openai_messages.append({
                "role": msg["role"],
                "content": msg["content"]
                # Исключаем timestamp, так как OpenAI его не принимает
            })

        return openai_messages

    async def get_chat_messages_with_timestamp(self, chat_id: str) -> List[Dict]:
        """Возвращает полные сообщения с timestamp (для внутреннего использования)"""
        chat = await self.get_chat(chat_id)
        return chat['messages'] if chat else []

    async def optimize_history(self, chat_id: str, max_messages: int):
        chat = await self.get_chat(chat_id)
        if chat and len(chat['messages']) > max_messages + 1:
            # Оставляем системное сообщение и последние N сообщений
            optimized_messages = [chat['messages'][0]] + chat['messages'][-(max_messages - 1):]

            await self.chats.update_one(
                {'_id': chat_id},
                {'$set': {'messages': optimized_messages}}
            )

    async def _schedule_chat_deletion(self, chat_id: str):
        """Планирует удаление завершенного чата через 1 час"""
        import asyncio

        async def delete_chat():
            # await asyncio.sleep(3600)  # 1 час
            await self.chats.delete_one({'_id': chat_id})

        asyncio.create_task(delete_chat())

    async def cleanup_completed_chats(self):
        """Немедленно удаляет все завершенные чаты"""
        result = await self.chats.delete_many({'status': 'completed'})
        return result.deleted_count

    async def get_active_chats_count(self) -> int:
        return await self.chats.count_documents({'status': 'active'})