from typing import AsyncGenerator

from config import Config
from src.application.use_cases.factory.UseCaseFactory import UseCaseFactory
from src.core.entities.QueryEntities import QueryRequest, LLMResponse, LLMStreamResponse


class APIApplication:
    def __init__(self, config: Config):
        self.config = config
        self.use_case = None

    async def initialize(self):
        """Асинхронная инициализация"""
        self.use_case = await UseCaseFactory.create_burnout_survey_use_case(
            self.config.MONGODB_CONNECTION_STRING
        )

    async def query(self, query_request: QueryRequest) -> LLMResponse:
        """Универсальный метод для создания или продолжения диалога"""
        if not self.use_case:
            await self.initialize()


        response = await self.use_case.execute(query_request)
        print(f"chat_id: {response.chat_id}\ncontent: {response.content}\n"
              f"total_questions: {response.total_questions}\nquestion_count: {response.question_count}\n"
              f"is_completed: {response.is_completed}")

        return response

    async def query_stream(self, query_request: QueryRequest) -> AsyncGenerator[LLMStreamResponse, None]:
        """Streaming версия запроса"""
        if not self.use_case:
            await self.initialize()

        if hasattr(self.use_case, 'execute_stream'):
            async for chunk in self.use_case.execute_stream(query_request):
                yield chunk
        else:
            response = await self.use_case.execute(query_request)
            yield LLMStreamResponse(
                content_chunk=response.content,
                chat_id=response.chat_id,
                is_completed=response.is_completed,
                question_count=response.question_count,
                total_questions=response.total_questions,
                is_final_chunk=True
            )