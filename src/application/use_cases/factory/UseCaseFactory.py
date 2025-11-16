from src.application.use_cases.EmotionalUseCase import EmotionalUseCase
from src.application.use_cases.QueryLLMUseCase import QueryLLMUseCase
from src.core.interfaces.IChatStorage import IChatStorage
from src.core.interfaces.IEmotionalClassification import IEmotionalClassification
from src.core.interfaces.ILLMProvider import ILLMProvider
from src.infrastructure.emotion_classification.EmotionClassification import EmotionalClassification
from src.infrastructure.llm.DeepSeekLLM import DeepSeekLLM
from src.infrastructure.mongodb_store.MongoDBChatStorage import MongoDBChatStorage


class UseCaseFactory:
    @staticmethod
    async def create_burnout_survey_use_case(mongo_connection_string: str) -> QueryLLMUseCase:
        llm_provider: ILLMProvider = DeepSeekLLM()
        chat_storage: IChatStorage = MongoDBChatStorage(mongo_connection_string)
        emotional_classification: IEmotionalClassification = EmotionalClassification()
        emotional_use_case = EmotionalUseCase(emotional_classification)

        return QueryLLMUseCase(
            llm_provider=llm_provider,
            chat_storage=chat_storage,
            emotional_use_case=emotional_use_case
        )