import asyncio
import sys
import os
from datetime import datetime

from src.application.use_cases.QueryLLMUseCase import QueryLLMUseCase, UseCaseFactory
from src.core.entities.QueryEntitiesTODO import QueryRequest, LLMResponse
# from src.core.entities.UserEntities import UserPsychStatus

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from config import Config

# src/application/api_app.py
import sys
import os
from src.application.use_cases.QueryLLMUseCase import QueryLLMUseCase, UseCaseFactory
from src.core.entities.QueryEntitiesTODO import QueryRequest, LLMResponse

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from config import Config


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

if __name__ == "__main__":
    # # Пример 1: Позитивный статус сотрудника
    # psych_status_1 = UserPsychStatus(
    #     date=datetime(2024, 1, 15),
    #     summary="Сотрудник демонстрирует высокий уровень мотивации и вовлеченности. Отлично справляется с рабочими задачами, проявляет инициативу. Эмоциональное состояние стабильное, наблюдается позитивный настрой.",
    #     recommendations="Рекомендуется продолжить текущую поддержку. Рассмотреть возможность участия в менторской программе. Поощрить за активную позицию.",
    #     status=["высокая мотивация", "стабильное эмоциональное состояние", "проактивность", "хорошая работоспособность"]
    # )
    #
    # # Пример 2: Средний статус с небольшими проблемами
    # psych_status_2 = UserPsychStatus(
    #     date=datetime(2024, 1, 10),
    #     summary="Наблюдается умеренный уровень стресса, связанный с текущими проектами. Сотрудник испытывает некоторые трудности с тайм-менеджментом, но в целом справляется с нагрузкой.",
    #     recommendations="Провести коучинг по управлению временем. Рассмотреть возможность временного снижения нагрузки. Увеличить частность check-in встреч.",
    #     status=["умеренный стресс", "проблемы с тайм-менеджментом", "средняя работоспособность", "требуется поддержка"]
    # )
    #
    # # Пример 3: Сотрудник в состоянии выгорания
    # psych_status_3 = UserPsychStatus(
    #     date=datetime(2024, 1, 5),
    #     summary="Выявлены признаки профессионального выгорания. Снижена продуктивность, наблюдается эмоциональное истощение. Сотрудник испытывает трудности с концентрацией.",
    #     recommendations="Срочно организовать консультацию с психологом. Предоставить дополнительные дни отдыха. Временно снизить нагрузку. Рассмотреть возможность ротации задач.",
    #     status=["выгорание", "эмоциональное истощение", "сниженная продуктивность", "тревожность",
    #             "требуется немедленная помощь"]
    # )
    #
    # example_psych_statuses = [
    #     psych_status_1, psych_status_2, psych_status_3
    # ]
    query_system = QuerySystem()
    asyncio.run(query_system.query(QueryRequest(user_input="7", chat_id="39027a70-ab32-48fa-9907-1171e1867b40")))


