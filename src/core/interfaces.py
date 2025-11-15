from abc import ABC, abstractmethod
from typing import List, Optional, Dict, AsyncGenerator

from src.core.entities.QueryEntities import Document, VectorSearchResult
from src.core.entities.UserEntities import ListUserPsychStatus


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

    @abstractmethod
    async def generate_response_stream(self, messages: list) -> AsyncGenerator[str, None]:
        pass


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


class IFileReader(ABC):
    @abstractmethod
    def read_files(self, directory_path: str) -> List[Document]:
        pass


class IEmbeddingService(ABC):
    @abstractmethod
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        pass