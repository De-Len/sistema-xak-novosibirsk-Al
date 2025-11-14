from abc import ABC, abstractmethod
from typing import List, Optional, Dict

from src.core.entities.QueryEntities import DialogueEntity, MessageEntity
from src.core.entities.QueryEntitiesTODO import Document, VectorSearchResult
from src.core.entities.UserEntities import UserEntity, UserPsychStatus


class IVectorStore(ABC):
    @abstractmethod
    async def add_documents(self, documents: List[Document]) -> None:
        pass

    @abstractmethod
    async def search(self, query: str, k: int = 3) -> List[VectorSearchResult]:
        pass

    @abstractmethod
    async def get_all_documents(self) -> List[Document]:
        pass


class ILLMProvider(ABC):
    @abstractmethod
    async def generate_response(self, messages: list) -> str:
        pass


class IChatStorage(ABC):
    @abstractmethod
    def create_chat(self, max_questions: int) -> str:
        pass

    @abstractmethod
    def get_chat(self, chat_id: str) -> Optional[Dict]:
        pass

    @abstractmethod
    def add_message(self, chat_id: str, role: str, content: str):
        pass

    @abstractmethod
    def increment_question_count(self, chat_id: str):
        pass

    @abstractmethod
    def is_chat_completed(self, chat_id: str) -> bool:
        pass

    @abstractmethod
    def get_chat_messages(self, chat_id: str) -> list:
        pass

class IFileReader(ABC):
    @abstractmethod
    def read_files(self, directory_path: str) -> List[Document]:
        pass


class IEmbeddingService(ABC):
    @abstractmethod
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        pass


# NEW
class IUserRepository(ABC):
    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[UserEntity]:
        pass

    @abstractmethod
    def get_psych_status(self, user_id: int) -> Optional[UserPsychStatus]:
        pass


class IDialogueRepository(ABC):
    @abstractmethod
    def create_dialogue(self, dialogue: DialogueEntity) -> DialogueEntity:
        pass

    @abstractmethod
    def get_user_dialogues(self, user_id: int) -> List[DialogueEntity]:
        pass

    @abstractmethod
    def get_active_dialogue(self, user_id: int) -> Optional[DialogueEntity]:
        pass

    @abstractmethod
    def deactivate_dialogue(self, dialogue_id: int) -> None:
        pass

    @abstractmethod
    def update_dialogue(self, dialogue: DialogueEntity) -> None:
        pass


class IMessageRepository(ABC):
    @abstractmethod
    def add_message(self, message: MessageEntity) -> MessageEntity:
        pass

    @abstractmethod
    def get_dialogue_messages(self, dialogue_id: int, limit: Optional[int] = None) -> List[MessageEntity]:
        pass

    @abstractmethod
    def get_dialogue_messages_count(self, dialogue_id: int) -> int:
        pass
