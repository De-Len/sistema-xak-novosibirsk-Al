import uuid
from typing import List
import asyncio
import chromadb
from chromadb.config import Settings

from src.core.entities.QueryEntitiesTODO import Document, VectorSearchResult
from src.core.interfaces import IVectorStore
from src.application.services.EmbeddingService import EmbeddingService

class ChromaVectorStore(IVectorStore):
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection("documents_ru")
        self.embedding_service = EmbeddingService()
        self._cached_documents: List[Document] | None = None
        self._lock = asyncio.Lock()

    async def add_documents(self, documents: List[Document]) -> None:
        if not documents:
            return

        texts = [doc.content for doc in documents]
        embeddings = await self.embedding_service.get_embeddings(texts)

        # ChromaDB sync API → оборачиваем в to_thread
        await asyncio.to_thread(
            self.collection.add,
            documents=texts,
            embeddings=embeddings,
            metadatas=[doc.metadata for doc in documents],
            ids=[str(uuid.uuid4()) for _ in documents]
        )

        async with self._lock:
            self._cached_documents = None

    async def search(self, query: str, k: int = 3) -> List[VectorSearchResult]:
        query_embedding = await self.embedding_service.get_embeddings([query])

        results = await asyncio.to_thread(
            self.collection.query,
            query_embeddings=query_embedding,
            n_results=k
        )

        search_results = []
        if results['documents'] and results['documents'][0]:
            for i, (doc_content, metadata, distance) in enumerate(zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0] if results['distances'] else [1.0] * len(results['documents'][0])
            )):
                document = Document(
                    content=doc_content,
                    metadata=metadata,
                    id=results['ids'][0][i] if results['ids'] else None
                )
                similarity = 1 - distance
                search_results.append(VectorSearchResult(
                    document=document,
                    similarity_score=similarity
                ))
        return search_results

    async def get_all_documents(self) -> List[Document]:
        async with self._lock:
            if self._cached_documents is not None:
                return self._cached_documents

            results = await asyncio.to_thread(self.collection.get)

            documents = [
                Document(content=doc, metadata=meta, id=id_)
                for doc, meta, id_ in zip(
                    results["documents"], results["metadatas"], results["ids"]
                )
            ]
            self._cached_documents = documents
            return documents