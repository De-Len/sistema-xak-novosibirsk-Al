from abc import ABC, abstractmethod
from typing import List

from src.core.entities.QueryEntities import Document, VectorSearchResult


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



