from typing import Optional
from src.core.entities import LLMResponse, QueryRequest, VectorSearchResult
from src.core.interfaces import IVectorStore, ILLMProvider


class QueryLLMUseCase:
    def __init__(self, vector_store: IVectorStore, llm_provider: ILLMProvider):
        self.vector_store = vector_store
        self.llm_provider = llm_provider

    async def execute(self, query_request: QueryRequest) -> LLMResponse:
        """
        Асинхронный запрос к LLM с контекстом из релевантных документов
        """
        # 1. Асинхронный поиск релевантных документов
        search_results: list[VectorSearchResult] = await self.vector_store.search(
            query=query_request.question,
            k=query_request.top_k
        )

        # 2. Формирование контекста
        context = self._build_context(search_results)

        # 3. Асинхронная генерация ответа LLM
        response = await self.llm_provider.generate_response(
            prompt=query_request.question,
            context=context
        )

        # 4. Возврат LLMResponse
        return response

    def _build_context(self, search_results: list[VectorSearchResult]) -> str:
        if not search_results:
            return "Контекст не найден."

        context_parts = [
            f"Документ {i} (схожесть: {result.similarity_score:.2f}):\n{result.document.content}"
            for i, result in enumerate(search_results, 1)
        ]
        return "\n\n".join(context_parts)