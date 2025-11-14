import asyncio
from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer

from src.core.interfaces import IEmbeddingService


class EmbeddingService(IEmbeddingService):
    def __init__(self, model_path: str = None):
        if model_path is None:
            from config import Config
            model_path = Config.EMBEDDING_MODEL
        self.model = SentenceTransformer(model_path)

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Асинхронная генерация эмбеддингов.
        Оборачиваем sync метод model.encode через asyncio.to_thread
        """
        if not texts:
            return []

        embeddings = await asyncio.to_thread(self.model.encode, texts)
        return embeddings.tolist()