# src/application/use_cases/QueryLLMUseCase.py
from typing import AsyncGenerator, Union
import json

from src.core.entities.QueryEntitiesTODO import QueryRequest, LLMResponse, LLMStreamResponse
from src.core.entities.UserEntities import ListUserPsychStatus
from src.core.interfaces import ILLMProvider, IChatStorage
from src.infrastructure.burnout_analysis_parser.BurnoutAnalysisService import BurnoutAnalysisService
from src.infrastructure.llm.DeepSeekLLM import DeepSeekLLM
from src.infrastructure.mongodb_store.MongoDBChatStorage import MongoDBChatStorage


class QueryLLMUseCase:
    def __init__(self, llm_provider: ILLMProvider, chat_storage: IChatStorage):
        self.llm_provider = llm_provider
        self.chat_storage = chat_storage
        self.analysis_service = BurnoutAnalysisService()

        # Промпт для анализа результатов
        self.analysis_prompt = """
            ТЫ ДОЛЖЕН ВЫВЕСТИ ТОЛЬКО JSON БЕЗ ЛЮБЫХ ДОПОЛНИТЕЛЬНЫХ СЛОВ, КОММЕНТАРИЕВ ИЛИ ФОРМАТИРОВАНИЯ.
            Ты профессиональный психолог. Проанализируй полученные ответы на опрос профессионального выгорания (MBI) и предоставь результаты.

            Шкалы оценки:
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
              "recommendations": ["рекомендация emotional_exhaustion", "рекомендация depersonalization", "рекомендация reduction_of_achievements", "Общая рекомендация"]
            }
            НЕ ПИШИ НИКАКИХ ПРЕДИСЛОВИЙ, КОММЕНТАРИЕВ, ВОПРОСОВ ИЛИ ЗАКЛЮЧЕНИЙ.
            НЕ ИСПОЛЬЗУЙ MARKDOWN ФОРМАТИРОВАНИЕ.
            ВЫВЕДИ ТОЛЬКО ЧИСТЫЙ JSON           
            """

    async def execute(self, query_request: QueryRequest) -> LLMResponse:
        # Определяем или создаем chat_id
        chat_id = await self._get_or_create_chat_id(query_request)

        # Получаем текущее состояние чата
        chat = await self.chat_storage.get_chat(chat_id)
        current_question_count = chat['question_count'] if chat else 0

        print(
            f"🔍 DEBUG: Начало execute. Вопросов: {current_question_count}, Пользователь: {query_request.user_input[:50]}...")

        # Добавляем сообщение пользователя
        await self.chat_storage.add_message(chat_id, "user", query_request.user_input)

        # Оптимизируем историю если нужно
        await self.chat_storage.optimize_history(chat_id, query_request.max_history_messages)

        # Получаем полную историю для анализа
        full_messages = await self.chat_storage.get_chat_messages_with_timestamp(chat_id)

        # Определяем, нужно ли использовать анализ
        should_use_analysis = (
                current_question_count == 7
        )

        print(f"🔍 DEBUG: should_use_analysis = {should_use_analysis}")

        # Получаем сообщения для контекста
        if should_use_analysis:
            print("🔍 DEBUG: Используем промпт для анализа")
            messages = await self._prepare_messages_for_analysis(chat_id)
        else:
            print("🔍 DEBUG: Используем обычный промпт")
            messages = await self.chat_storage.get_chat_messages(chat_id)

        # Получаем ответ от LLM
        assistant_response = await self.llm_provider.generate_response(messages)

        print(f"🔍 DEBUG: Ответ ассистента: {assistant_response[:100]}...")

        # Парсим результат если это анализ
        final_response = assistant_response
        is_analysis = False

        if should_use_analysis:
            parsed_result = self.analysis_service.parse_llm_response(assistant_response)
            if parsed_result:
                final_response = parsed_result
                is_analysis = True
                print("✅ Результат анализа успешно распарсен")
            else:
                print("❌ Не удалось распарсить результат анализа, используем сырой ответ")

        # Добавляем ответ ассистента и увеличиваем счетчик
        await self.chat_storage.add_message(chat_id, "assistant",
                                            final_response.to_json() if is_analysis else assistant_response)
        await self.chat_storage.increment_question_count(chat_id)

        # Проверяем статус завершения
        is_completed = await self.chat_storage.is_chat_completed(chat_id)

        # Получаем текущий счетчик вопросов
        updated_chat = await self.chat_storage.get_chat(chat_id)
        question_count = updated_chat['question_count'] if updated_chat else 0

        print(f"🔍 DEBUG: Конец execute. Вопросов стало: {question_count}, Завершен: {is_completed}")

        return LLMResponse(
            content=final_response,
            chat_id=chat_id,
            is_completed=is_completed,
            question_count=question_count,
            total_questions=query_request.max_questions,
            is_analysis=is_analysis
        )

    async def execute_stream(self, query_request: QueryRequest) -> AsyncGenerator[LLMStreamResponse, None]:
        """Streaming версия execute"""
        # Определяем или создаем chat_id
        chat_id = await self._get_or_create_chat_id(query_request)

        # Получаем текущее состояние чата
        chat = await self.chat_storage.get_chat(chat_id)
        current_question_count = chat['question_count'] if chat else 0

        print(
            f"🔍 DEBUG: Начало execute_stream. Вопросов: {current_question_count}, Пользователь: {query_request.user_input[:50]}...")

        # Добавляем сообщение пользователя
        await self.chat_storage.add_message(chat_id, "user", query_request.user_input)

        # Оптимизируем историю если нужно
        await self.chat_storage.optimize_history(chat_id, query_request.max_history_messages)

        # Получаем полную историю для анализа
        full_messages = await self.chat_storage.get_chat_messages_with_timestamp(chat_id)

        # Определяем, нужно ли использовать анализ
        should_use_analysis = (
                current_question_count == 7 and  # Уже задано 7 вопросов
                len(full_messages) > 1 and
                full_messages[-1]["role"] == "user"  # Последнее сообщение - ответ пользователя
        )

        print(f"🔍 DEBUG: should_use_analysis = {should_use_analysis}")

        # Получаем сообщения для контекста
        if should_use_analysis:
            print("🔍 DEBUG: Используем промпт для анализа")
            messages = await self._prepare_messages_for_analysis(chat_id)
        else:
            print("🔍 DEBUG: Используем обычный промпт")
            messages = await self.chat_storage.get_chat_messages(chat_id)

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
                is_final_chunk=False,
                is_analysis=should_use_analysis
            )

        # Парсим результат если это анализ
        final_response = full_response
        is_analysis = should_use_analysis

        if should_use_analysis:
            parsed_result = self.analysis_service.parse_llm_response(full_response)
            if parsed_result:
                final_response = parsed_result.to_json()
                print("✅ Результат анализа успешно распарсен")
            else:
                print("❌ Не удалось распарсить результат анализа, используем сырой ответ")

        # После завершения streaming - сохраняем полный ответ
        await self.chat_storage.add_message(chat_id, "assistant", final_response)

        # Увеличиваем счетчик вопросов
        await self.chat_storage.increment_question_count(chat_id)

        # Проверяем статус завершения
        is_completed = await self.chat_storage.is_chat_completed(chat_id)

        # Получаем обновленный счетчик
        updated_chat = await self.chat_storage.get_chat(chat_id)
        question_count = updated_chat['question_count'] if updated_chat else 0

        print(f"🔍 DEBUG: Конец execute_stream. Вопросов стало: {question_count}, Завершен: {is_completed}")

        # Отправляем финальный chunk
        yield LLMStreamResponse(
            content_chunk="",
            chat_id=chat_id,
            is_completed=is_completed,
            question_count=question_count,
            total_questions=query_request.max_questions,
            is_final_chunk=True,
            is_analysis=is_analysis
        )

    async def _prepare_messages_for_analysis(self, chat_id: str) -> list:
        """Подготавливает сообщения для анализа результатов"""
        # Получаем только диалог (вопросы и ответы) без системного промпта
        all_messages = await self.chat_storage.get_chat_messages_with_timestamp(chat_id)

        dialog_messages = []
        for msg in all_messages:
            if msg["role"] in ["user", "assistant"]:
                dialog_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

        # Добавляем промпт для анализа в начало
        analysis_messages = [
            {"role": "system", "content": self.analysis_prompt},
            *dialog_messages
        ]

        print(f"🔍 DEBUG: Для анализа подготовлено {len(analysis_messages)} сообщений")
        return analysis_messages

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