import uuid
from datetime import datetime
from typing import Dict, Optional

from src.core.interfaces import IChatStorage


class InMemoryChatStorage(IChatStorage):
    def __init__(self):
        self.chats: Dict[str, Dict] = {}
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

    def create_chat(self, max_questions: int) -> str:
        chat_id = str(uuid.uuid4())
        self.chats[chat_id] = {
            'id': chat_id,
            'created_at': datetime.now(),
            'messages': [
                {
                    "role": "system",
                    "content": self.system_prompt
                }
            ],
            'question_count': 0,
            'max_questions': max_questions,
            'status': 'active'
        }
        return chat_id

    def get_chat(self, chat_id: str) -> Optional[Dict]:
        return self.chats.get(chat_id)

    def add_message(self, chat_id: str, role: str, content: str):
        chat = self.get_chat(chat_id)
        if chat and chat['status'] == 'active':
            chat['messages'].append({"role": role, "content": content})

    def increment_question_count(self, chat_id: str):
        chat = self.get_chat(chat_id)
        if chat:
            chat['question_count'] += 1
            if chat['question_count'] >= chat['max_questions']:
                chat['status'] = 'completed'

    def is_chat_completed(self, chat_id: str) -> bool:
        chat = self.get_chat(chat_id)
        return chat and chat['status'] == 'completed'

    def get_chat_messages(self, chat_id: str) -> list:
        chat = self.get_chat(chat_id)
        return chat['messages'] if chat else []

    def optimize_history(self, chat_id: str, max_messages: int):
        """Ограничивает размер истории сообщений"""
        chat = self.get_chat(chat_id)
        if chat and len(chat['messages']) > max_messages + 1:
            chat['messages'] = [chat['messages'][0]] + chat['messages'][-(max_messages - 1):]