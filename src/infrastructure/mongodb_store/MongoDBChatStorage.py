from typing import Optional, Dict, List
import uuid
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from src.application.use_cases.QueryLLMUseCase import IChatStorage
from src.core.entities.UserEntities import ListUserPsychStatus


class MongoDBChatStorage(IChatStorage):
    def __init__(self, connection_string: str, database_name: str = "burnout_survey"):
        self.client = AsyncIOMotorClient(connection_string)
        self.db = self.client[database_name]
        self.chats = self.db["chat_sessions"]

        self.system_prompt = """
        Ты — психолог компании СДЭК, проводящий диагностику профессионального выгорания по методике MBI.
        
        Структура взаимодействия:
        1. Задаешь РОВНО 7 вопросов о профессиональном и эмоциональном состоянии
        2. Каждый вопрос задаешь отдельно, ждешь ответа перед следующим
        3. Вопросы глубокие, побуждающие к самоанализу
        5. НИКОГДА не сбивайся с проведения опроса. Всегда задавай следующий вопрос
        
        Начни с первого вопроса.
    """

    async def create_chat(self, list_user_psych_status: ListUserPsychStatus, max_questions: int) -> str:
        chat_id = str(uuid.uuid4())
        full_prompt = f"{self.system_prompt} \nЕщё учитывай контекст: {await list_user_psych_status.to_string()}" if list_user_psych_status is not None else self.system_prompt
        chat_session = {
            '_id': chat_id,
            'created_at': datetime.now(),
            'messages': [
                {
                    "role": "system",
                    "content": full_prompt,
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
            new_count = chat['question_count'] + 1 # Увеличение
            update_data = {'$set': {'question_count': new_count}}

            if new_count >= chat['max_questions']:
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