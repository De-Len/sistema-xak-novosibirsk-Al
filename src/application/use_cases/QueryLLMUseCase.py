from src.core.entities.QueryEntitiesTODO import QueryRequest, LLMResponse
from src.core.interfaces import ILLMProvider, IChatStorage
from src.infrastructure.llm.DeepSeekLLM import DeepSeekLLM
from src.infrastructure.llm.InMemoryChatStorage import InMemoryChatStorage


class QueryLLMUseCase:
    pass


class UseCaseFactory:
    @staticmethod
    def create_burnout_survey_use_case() -> QueryLLMUseCase:
        llm_provider = DeepSeekLLM()
        chat_storage = InMemoryChatStorage()
        return QueryLLMUseCase(llm_provider, chat_storage)
    
    
class QueryLLMUseCase:
    def __init__(self, llm_provider: ILLMProvider, chat_storage: IChatStorage):
        self.llm_provider = llm_provider
        self.chat_storage = chat_storage

    async def execute(self, query_request: QueryRequest) -> LLMResponse:
        # Определяем или создаем chat_id
        chat_id = await self._get_or_create_chat_id(query_request)

        # Добавляем сообщение пользователя
        self.chat_storage.add_message(chat_id, "user", query_request.user_input)

        # Оптимизируем историю если нужно
        if hasattr(self.chat_storage, 'optimize_history'):
            self.chat_storage.optimize_history(chat_id, query_request.max_history_messages)

        # Получаем ответ от LLM
        messages = self.chat_storage.get_chat_messages(chat_id)
        assistant_response = await self.llm_provider.generate_response(messages)

        # Добавляем ответ ассистента и увеличиваем счетчик
        self.chat_storage.add_message(chat_id, "assistant", assistant_response)
        self.chat_storage.increment_question_count(chat_id)

        # Проверяем статус завершения
        is_completed = self.chat_storage.is_chat_completed(chat_id)

        # Получаем текущий счетчик вопросов
        chat = self.chat_storage.get_chat(chat_id)
        question_count = chat['question_count'] if chat else 0

        return LLMResponse(
            content=assistant_response,
            chat_id=chat_id,
            is_completed=is_completed,
            question_count=question_count,
            total_questions=query_request.max_questions
        )

    async def _get_or_create_chat_id(self, request: QueryRequest) -> str:
        if request.chat_id and self.chat_storage.get_chat(request.chat_id):
            return request.chat_id
        else:
            return self.chat_storage.create_chat(request.max_questions)