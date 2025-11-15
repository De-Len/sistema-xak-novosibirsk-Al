from abc import ABC, abstractmethod
from typing import Optional, Dict, List

from src.core.entities.user_entites.ListUserPsychStatus import ListUserPsychStatus


class IChatStorage(ABC):
    @abstractmethod
    async def create_chat(self, list_user_psych_status: Optional[ListUserPsychStatus], max_questions: int) -> str:
        pass

    @abstractmethod
    async def get_chat(self, chat_id: str) -> Optional[Dict]:
        pass

    @abstractmethod
    async def add_message(self, chat_id: str, role: str, content: str) -> None:
        pass

    @abstractmethod
    async def increment_question_count(self, chat_id: str) -> None:
        pass

    @abstractmethod
    async def is_chat_completed(self, chat_id: str) -> bool:
        pass

    @abstractmethod
    async def get_chat_messages(self, chat_id: str) -> List[Dict]:
        pass

    @abstractmethod
    async def get_chat_messages_with_timestamp(self, chat_id: str) -> List[Dict]:
        pass

    @abstractmethod
    async def optimize_history(self, chat_id: str, max_messages: int) -> None:
        pass