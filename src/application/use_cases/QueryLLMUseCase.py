from typing import AsyncGenerator

from src.core.entities.QueryEntitiesTODO import QueryRequest, LLMResponse, LLMStreamResponse
from src.core.entities.UserEntities import ListUserPsychStatus
from src.core.interfaces import ILLMProvider, IChatStorage
from src.infrastructure.llm.DeepSeekLLM import DeepSeekLLM
from src.infrastructure.mongodb_store.MongoDBChatStorage import MongoDBChatStorage


class QueryLLMUseCase:
    def __init__(self, llm_provider: ILLMProvider, chat_storage: IChatStorage):
        self.llm_provider = llm_provider
        self.chat_storage = chat_storage

        # Промпт для анализа результатов
        self.analysis_prompt = """
Есть шкалы оценки:
- Эмоциональное истощение (0-54): 0-15 низкий, 16-24 средний, 25+ высокий
- Деперсонализация (0-30): 0-5 низкий, 6-10 средний, 11+ высокий
- Редукция проф. достижений (0-48): 0-30 низкий, 31-36 средний, 37+ высокий
- Системный индекс = (ЭИ + ДП + РПД) / 132

Формат твоего ответа (В СТРОГОМ JSON-формате):
{
  "emotional_exhaustion": 0-54,
  "depersonalization": 0-30, 
  "reduction_of_achievements": 0-48,
  "burnout_index": 0.0-1.0,
  "recommendations": ["рекомендация emotional_exhaustion", "рекомендация depersonalization", "рекомендация reduction_of_achievements, "Общая рекомендация"]
}
НЕ ВЫВОДИ БОЛЬШЕ НИЧЕГО КРОМЕ JSON
"""

    async def execute(self, query_request: QueryRequest) -> LLMResponse:
        # Определяем или создаем chat_id
        chat_id = await self._get_or_create_chat_id(query_request)

        # Получаем текущее состояние чата
        chat = await self.chat_storage.get_chat(chat_id)
        current_question_count = chat['question_count'] if chat else 0

        # Добавляем сообщение пользователя
        await self.chat_storage.add_message(chat_id, "user", query_request.user_input)

        # Оптимизируем историю если нужно
        await self.chat_storage.optimize_history(chat_id, query_request.max_history_messages)

        # Получаем сообщения для контекста
        messages = await self._prepare_messages_for_llm(chat_id, current_question_count)

        # Получаем ответ от LLM
        assistant_response = await self.llm_provider.generate_response(messages)

        # Добавляем ответ ассистента и увеличиваем счетчик
        await self.chat_storage.add_message(chat_id, "assistant", assistant_response)
        await self.chat_storage.increment_question_count(chat_id)

        # Проверяем статус завершения
        is_completed = await self.chat_storage.is_chat_completed(chat_id)

        # Получаем текущий счетчик вопросов
        updated_chat = await self.chat_storage.get_chat(chat_id)
        question_count = updated_chat['question_count'] if updated_chat else 0

        return LLMResponse(
            content=assistant_response,
            chat_id=chat_id,
            is_completed=is_completed,
            question_count=question_count,
            total_questions=query_request.max_questions
        )

    async def execute_stream(self, query_request: QueryRequest) -> AsyncGenerator[LLMStreamResponse, None]:
        """Streaming версия execute"""
        # Определяем или создаем chat_id
        chat_id = await self._get_or_create_chat_id(query_request)

        # Получаем текущее состояние чата
        chat = await self.chat_storage.get_chat(chat_id)
        current_question_count = chat['question_count'] if chat else 0

        # Добавляем сообщение пользователя
        await self.chat_storage.add_message(chat_id, "user", query_request.user_input)

        # Оптимизируем историю если нужно
        await self.chat_storage.optimize_history(chat_id, query_request.max_history_messages)

        # Получаем сообщения для контекста (с учетом анализа на последнем вопросе)
        print(f"Количество вопросов: {current_question_count}")
        messages = await self._prepare_messages_for_llm(chat_id, current_question_count)

        # Собираем полный ответ по частям
        full_response = ""

        # Генерируем streaming ответ
        async for chunk in self.llm_provider.generate_response_stream(messages):
            full_response += chunk

            # Отправляем каждую часть
            yield LLMStreamResponse(
                content_chunk=chunk,
                chat_id=chat_id,
                is_completed=False,
                question_count=current_question_count,
                total_questions=query_request.max_questions,
                is_final_chunk=False
            )

        # После завершения streaming - сохраняем полный ответ
        await self.chat_storage.add_message(chat_id, "assistant", full_response)

        # Увеличиваем счетчик вопросов
        await self.chat_storage.increment_question_count(chat_id)

        # Проверяем статус завершения
        is_completed = await self.chat_storage.is_chat_completed(chat_id)

        # Получаем обновленный счетчик
        updated_chat = await self.chat_storage.get_chat(chat_id)
        question_count = updated_chat['question_count'] if updated_chat else 0

        # Отправляем финальный chunk
        yield LLMStreamResponse(
            content_chunk="",
            chat_id=chat_id,
            is_completed=is_completed,
            question_count=question_count,
            total_questions=query_request.max_questions,
            is_final_chunk=True
        )

    async def _prepare_messages_for_llm(self, chat_id: str, current_question_count: int) -> list:
        """Подготавливает сообщения для LLM в зависимости от текущего вопроса"""
        all_messages = await self.chat_storage.get_chat_messages(chat_id)

        # Если это последний вопрос (7-й, т.к. счетчик увеличится после ответа)
        if current_question_count == 7:  # 7-й вопрос -> следующий будет 8-й (анализ)
            # Фильтруем только вопросы и ответы (исключаем системный промпт)
            dialog_messages = [
                msg for msg in all_messages
                if msg["role"] in ["user", "assistant"]
            ]

            # Добавляем промпт для анализа в начало
            analysis_messages = [
                {"role": "system", "content": self.analysis_prompt},
                *dialog_messages
            ]

            return analysis_messages
        else:
            # Для обычных вопросов используем все сообщения
            return all_messages

    async def _get_or_create_chat_id(self, request: QueryRequest) -> str:
        """Создает новый чат или возвращает существующий"""
        # Если передан chat_id и чат существует - используем его
        if request.chat_id:
            existing_chat = await self.chat_storage.get_chat(request.chat_id)
            if existing_chat:
                return request.chat_id

        # Иначе создаем новый чат с учетом list_user_psych_status
        return await self.chat_storage.create_chat(
            list_user_psych_status=request.list_user_psych_status,
            max_questions=request.max_questions
        )


class UseCaseFactory:
    @staticmethod
    async def create_burnout_survey_use_case(mongo_connection_string: str) -> QueryLLMUseCase:
        llm_provider = DeepSeekLLM()
        chat_storage = MongoDBChatStorage(mongo_connection_string)

        return QueryLLMUseCase(llm_provider, chat_storage)