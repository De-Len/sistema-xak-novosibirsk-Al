from src.core.entities.QueryEntitiesTODO import QueryRequest, LLMResponse
from src.core.entities.UserEntities import ListUserPsychStatus
from src.core.interfaces import ILLMProvider, IChatStorage
from src.infrastructure.llm.DeepSeekLLM import DeepSeekLLM
from src.infrastructure.mongodb_store.MongoDBChatStorage import MongoDBChatStorage

class QueryLLMUseCase:
    def __init__(self, llm_provider: ILLMProvider, chat_storage: IChatStorage):
        self.llm_provider = llm_provider
        self.chat_storage = chat_storage

    async def execute(self, query_request: QueryRequest) -> LLMResponse:
        # Определяем или создаем chat_id
        chat_id = await self._get_or_create_chat_id(query_request.list_user_psych_status, query_request)

        # Добавляем сообщение пользователя
        await self.chat_storage.add_message(chat_id, "user", query_request.user_input)

        # Оптимизируем историю если нужно
        await self.chat_storage.optimize_history(chat_id, query_request.max_history_messages)

        # Получаем ответ от LLM
        messages = await self.chat_storage.get_chat_messages(chat_id)
        assistant_response = await self.llm_provider.generate_response(messages)

        # Добавляем ответ ассистента и увеличиваем счетчик
        await self.chat_storage.add_message(chat_id, "assistant", assistant_response)
        await self.chat_storage.increment_question_count(chat_id)

        # Проверяем статус завершения
        is_completed = await self.chat_storage.is_chat_completed(chat_id)

        # Получаем текущий счетчик вопросов
        chat = await self.chat_storage.get_chat(chat_id)
        question_count = chat['question_count'] if chat else 0

        return LLMResponse(
            content=assistant_response,
            chat_id=chat_id,
            is_completed=is_completed,
            question_count=question_count,
            total_questions=query_request.max_questions
        )

    async def _get_or_create_chat_id(self, list_user_psych_status: ListUserPsychStatus, request: QueryRequest) -> str:
        if request.chat_id and await self.chat_storage.get_chat(request.chat_id):
            return request.chat_id
        else:
            return await self.chat_storage.create_chat(list_user_psych_status, request.max_questions)


class UseCaseFactory:
    @staticmethod
    async def create_burnout_survey_use_case(mongo_connection_string: str) -> QueryLLMUseCase:
        llm_provider = DeepSeekLLM()
        chat_storage = MongoDBChatStorage(mongo_connection_string)

        return QueryLLMUseCase(llm_provider, chat_storage)