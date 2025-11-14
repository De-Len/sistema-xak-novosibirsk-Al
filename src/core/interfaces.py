from abc import ABC, abstractmethod
from typing import List, Optional

from src.core.entities import Document, VectorSearchResult, LLMResponse


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
    async def generate_response(self, prompt: str, context: Optional[str] = None) -> LLMResponse:
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        pass


class IFileReader(ABC):
    @abstractmethod
    def read_files(self, directory_path: str) -> List[Document]:
        pass


class IEmbeddingService(ABC):
    @abstractmethod
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        pass