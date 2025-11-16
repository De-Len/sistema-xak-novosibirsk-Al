from typing import AsyncGenerator
from src.application.APIApplication import APIApplication
from src.core.entities.QueryEntities import LLMStreamResponse
from src.core.entities.QueryEntities import QueryRequest, LLMResponse
from config import Config


class QuerySystem:
    def __init__(self):
        self.config = Config()
        self.rag_app = APIApplication(self.config)
        print("\nSystem Ready!")

    async def initialize(self):
        """Асинхронная инициализация"""
        await self.rag_app.initialize()

    async def query(self, query_request: QueryRequest) -> LLMResponse | None:
        try:
            return await self.rag_app.query(query_request)
        except Exception as e:
            print(f"Error: {str(e)}")
            return None

    async def query_stream(self, query_request: QueryRequest) -> AsyncGenerator[LLMStreamResponse, None]:
        """Streaming запрос"""
        try:
            async for chunk in self.rag_app.query_stream(query_request):
                yield chunk
        except Exception as e:
            print(f"Error in streaming: {str(e)}")
            yield LLMStreamResponse(
                content_chunk=f"Error: {str(e)}",
                chat_id="",
                is_completed=True,
                question_count=0,
                total_questions=0,
                is_final_chunk=True
            )


