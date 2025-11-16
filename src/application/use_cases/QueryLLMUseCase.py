from typing import AsyncGenerator, List, Dict, Any

from src.application.use_cases.EmotionalUseCase import EmotionalUseCase
from src.core.entities.QueryEntities import (
    QueryRequest,
    LLMResponse,
    LLMStreamResponse,
)
from src.core.interfaces.IChatStorage import IChatStorage
from src.core.interfaces.ILLMProvider import ILLMProvider
from src.infrastructure.emotion_classification.EmotionClassification import EmotionalClassification
from src.infrastructure.extract_json_from_text.extract_json_from_text import extract_json_from_text

from src.infrastructure.llm.DeepSeekLLM import DeepSeekLLM
from src.infrastructure.mongodb_store.MongoDBChatStorage import MongoDBChatStorage


ANALYSIS_TRIGGER_QUESTION = 7


class QueryLLMUseCase:
    def __init__(self, llm_provider: ILLMProvider, chat_storage: IChatStorage):
        self.llm_provider = llm_provider
        self.chat_storage = chat_storage
        self.analysis_prompt = self._build_analysis_prompt()
        self.emotional_use_case = EmotionalUseCase(emotional_classification=EmotionalClassification())

    async def _extract_user_messages(self, full_messages: List[Dict[str, Any]]) -> List[str]:
        """Асинхронно извлекает массив строк только с запросами от пользователя"""
        return [
            message['content']
            for message in full_messages
            if message['role'] == 'user' and message['content'].strip()
        ]

    async def execute(self, query_request: QueryRequest) -> LLMResponse:
        chat_id, current_question_count = await self._get_or_init_chat(query_request)

        await self.chat_storage.add_message(chat_id, "user", query_request.user_input)
        await self.chat_storage.optimize_history(chat_id, query_request.max_history_messages)

        full_messages = await self.chat_storage.get_chat_messages_with_timestamp(chat_id)
        should_use_analysis = self._should_run_analysis(full_messages, current_question_count)

        if should_use_analysis:
            messages = await self._prepare_messages_for_analysis(full_messages, chat_id)

        else:
            messages = await self.chat_storage.get_chat_messages(chat_id)

        assistant_response = await self.llm_provider.generate_response(messages)

        final_content, is_analysis = self._process_analysis_if_needed(
            should_use_analysis, assistant_response
        )

        await self.chat_storage.add_message(
            chat_id,
            "assistant",
            final_content if is_analysis else final_content,
        )
        await self.chat_storage.increment_question_count(chat_id)

        updated_chat = await self.chat_storage.get_chat(chat_id)
        question_count = updated_chat["question_count"] if updated_chat else 0
        is_completed = await self.chat_storage.is_chat_completed(chat_id)

        return LLMResponse(
            content=final_content,
            chat_id=chat_id,
            is_completed=is_completed,
            question_count=question_count,
            total_questions=query_request.max_questions,
            is_analysis=is_analysis,
        )

    async def execute_stream(
        self, query_request: QueryRequest
    ) -> AsyncGenerator[LLMStreamResponse, None]:
        chat_id, current_question_count = await self._get_or_init_chat(query_request)

        await self.chat_storage.add_message(chat_id, "user", query_request.user_input)
        await self.chat_storage.optimize_history(chat_id, query_request.max_history_messages)

        full_messages = await self.chat_storage.get_chat_messages_with_timestamp(chat_id)
        should_use_analysis = self._should_run_analysis(full_messages, current_question_count)

        messages = (
            await self._prepare_messages_for_analysis(chat_id)
            if should_use_analysis
            else await self.chat_storage.get_chat_messages(chat_id)
        )

        full_response = ""
        async for chunk in self.llm_provider.generate_response_stream(messages):
            full_response += chunk
            yield LLMStreamResponse(
                content_chunk=chunk,
                chat_id=chat_id,
                is_completed=False,
                question_count=current_question_count,
                total_questions=query_request.max_questions,
                is_final_chunk=False,
                is_analysis=should_use_analysis,
            )

        final_content_str, is_analysis = self._finalize_stream_analysis(
            should_use_analysis, full_response
        )

        await self.chat_storage.add_message(chat_id, "assistant", final_content_str)
        await self.chat_storage.increment_question_count(chat_id)

        updated_chat = await self.chat_storage.get_chat(chat_id)
        question_count = updated_chat["question_count"] if updated_chat else 0
        is_completed = await self.chat_storage.is_chat_completed(chat_id)

        yield LLMStreamResponse(
            content_chunk="",
            chat_id=chat_id,
            is_completed=is_completed,
            question_count=question_count,
            total_questions=query_request.max_questions,
            is_final_chunk=True,
            is_analysis=is_analysis,
        )

    # ---------- Внутренние методы ----------

    @staticmethod
    def _build_analysis_prompt() -> str:
        return (
            "ТЫ ДОЛЖЕН ВЫВЕСТИ ТОЛЬКО JSON БЕЗ ЛЮБЫХ ДОПОЛНИТЕЛЬНЫХ СЛОВ, "
            "КОММЕНТАРИЕВ ИЛИ ФОРМАТИРОВАНИЯ.\n"
            "Ты профессиональный психолог. Проанализируй полученные ответы "
            "К каждому сообщению у тебя есть оценка самой высокой эмоции и её коэффициент от 0 до 1"
            "на опрос профессионального выгорания (MBI) и предоставь результаты.\n\n"
            "Шкалы оценки:\n"
            "- Эмоциональное истощение (0-54): 0-15 низкий, 16-24 средний, 25+ высокий\n"
            "- Деперсонализация (0-30): 0-5 низкий, 6-10 средний, 11+ высокий\n"
            "- Редукция проф. достижений (0-48): 0-30 низкий, 31-36 средний, 37+ высокий\n"
            "- Системный индекс = (ЭИ + ДП + РПД) / 132\n\n"
            "Формат ответа (СТРОГО JSON):\n"
            "{\n"
            '  "emotional_exhaustion": 0-54,\n'
            '  "depersonalization": 0-30,\n'
            '  "reduction_of_achievements": 0-48,\n'
            '  "burnout_index": 0.0-1.0,\n'
            '  "recommendations": [\n'
            '    "рекомендация emotional_exhaustion",\n'
            '    "рекомендация depersonalization",\n'
            '    "рекомендация reduction_of_achievements",\n'
            '    "Общая рекомендация"\n'
            "  ]\n"
            "}\n"
            "НЕ ПИШИ НИКАКИХ ПРЕДИСЛОВИЙ ИЛИ КОММЕНТАРИЕВ. ТОЛЬКО ЧИСТЫЙ JSON."
        )



    async def _get_or_init_chat(self, request: QueryRequest) -> tuple[str, int]:
        if request.chat_id:
            existing_chat = await self.chat_storage.get_chat(request.chat_id)
            if existing_chat:
                return request.chat_id, existing_chat.get("question_count", 0)

        chat_id = await self.chat_storage.create_chat(
            list_user_psych_status=request.list_user_psych_status,
            max_questions=request.max_questions,
        )
        return chat_id, 0

    @staticmethod
    def _should_run_analysis(full_messages: List[Dict[str, Any]], current_question_count: int) -> bool:
        if current_question_count != ANALYSIS_TRIGGER_QUESTION:
            return False
        if not full_messages:
            return False
        last = full_messages[-1]
        if last.get("role") == "user":
            return True

    async def _prepare_messages_for_analysis(self, full_messages, chat_id: str) -> List[Dict[str, str]]:
        all_messages = await self.chat_storage.get_chat_messages_with_timestamp(chat_id)
        user_messages = await self._extract_user_messages(full_messages)
        top_emotions = await self.emotional_use_case.analyze_messages_batch_top_emotions(user_messages)

        user_iter = iter(top_emotions)
        dialog_messages = []
        for msg in all_messages:
            if msg["role"] in {"user", "assistant"}:
                content = msg["content"]
                if msg["role"] == "user":
                    emo = next(user_iter, None)
                    if emo is not None:
                        content += f"\nЭмоциональная оценка сообщения: {emo}"
                dialog_messages.append({"role": msg["role"], "content": content})


        return [{"role": "system", "content": f"{self.analysis_prompt}.\n"
                                f"Ещё учитывай подсчёт эмоций на каждый вопрос:{top_emotions}"},
                *dialog_messages]

    def _process_analysis_if_needed(self, should_use_analysis: bool, assistant_response: str):
        if not should_use_analysis:
            return assistant_response, False

        parsed_result = extract_json_from_text(assistant_response)
        if not parsed_result:
            return assistant_response, False

        return parsed_result, True

    def _finalize_stream_analysis(self, should_use_analysis: bool, full_response: str) -> tuple[str, bool]:
        # TODO
        # if not should_use_analysis:
        #     return full_response, False
        #
        # parsed_result = self.analysis_service.parse_llm_response(full_response)
        # if not parsed_result:
        #     return full_response, False
        #
        # return parsed_result.to_json(), True
        return full_response, False


class UseCaseFactory:
    @staticmethod
    async def create_burnout_survey_use_case(mongo_connection_string: str) -> QueryLLMUseCase:
        llm_provider = DeepSeekLLM()
        chat_storage = MongoDBChatStorage(mongo_connection_string)
        return QueryLLMUseCase(llm_provider, chat_storage)