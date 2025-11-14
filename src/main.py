import sys
import os
from datetime import datetime

from src.application.use_cases.BuildVectorStoreUseCase import BuildVectorStoreUseCase
from src.application.use_cases.QueryLLMUseCase import QueryLLMUseCase, UseCaseFactory
from src.core.entities.QueryEntitiesTODO import QueryRequest, LLMResponse
from src.core.entities.UserEntities import UserPsychStatus
from src.infrastructure.file_reader.FileReader import FileReader
from src.infrastructure.llm.DeepSeekLLM import DeepSeekLLM
from src.infrastructure.vector_store.ChromaVectorStore import ChromaVectorStore

sys.path.append(os.path.dirname(os.path.dirname(__file__)))


from config import Config


class APIApplication:
    def __init__(self, config: Config):
        self.config = config
        self.use_case = UseCaseFactory.create_burnout_survey_use_case()


    def build_vector_store(self) -> int:
        """Построение векторной базы данных из txt файлов"""
        print(f"Building vector store from {self.config.DATA_DIRECTORY}...")
        document_count = self.build_vector_store_uc.execute(self.config.DATA_DIRECTORY)
        print(f"Vector store built successfully! Processed {document_count} documents.")
        return document_count

    async def query(self, query_request: QueryRequest) -> LLMResponse:
        """Запрос к LLM с RAG"""
        print(f"Processing query: {query_request.question}")
        response = await self.query_llm_uc.execute(query_request)

        print(f"\nResponse ({response.total_tokens} tokens):")
        print("=" * 50)
        print(response.content)
        print("=" * 50)

        return response

class QuerySystem:
    def __init__(self):
        self.rag_app = APIApplication(Config())
        existing_docs = self.rag_app.vector_store.get_all_documents()

        if not existing_docs:
            print("No documents found in vector store. Building...")
            self.rag_app.build_vector_store()
        else:
            print(f"Found documents in vector store.")

        # Интерактивный режим запросов
        print("\nRAG System Ready!")

    async def query(self, query_request: QueryRequest) -> LLMResponse | None:
        try:
            if query_request.question:
                llm_response = self.rag_app.query(query_request)
                return await llm_response

        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    # Пример 1: Позитивный статус сотрудника
    psych_status_1 = UserPsychStatus(
        date=datetime(2024, 1, 15),
        summary="Сотрудник демонстрирует высокий уровень мотивации и вовлеченности. Отлично справляется с рабочими задачами, проявляет инициативу. Эмоциональное состояние стабильное, наблюдается позитивный настрой.",
        recommendations="Рекомендуется продолжить текущую поддержку. Рассмотреть возможность участия в менторской программе. Поощрить за активную позицию.",
        status=["высокая мотивация", "стабильное эмоциональное состояние", "проактивность", "хорошая работоспособность"]
    )

    # Пример 2: Средний статус с небольшими проблемами
    psych_status_2 = UserPsychStatus(
        date=datetime(2024, 1, 10),
        summary="Наблюдается умеренный уровень стресса, связанный с текущими проектами. Сотрудник испытывает некоторые трудности с тайм-менеджментом, но в целом справляется с нагрузкой.",
        recommendations="Провести коучинг по управлению временем. Рассмотреть возможность временного снижения нагрузки. Увеличить частность check-in встреч.",
        status=["умеренный стресс", "проблемы с тайм-менеджментом", "средняя работоспособность", "требуется поддержка"]
    )

    # Пример 3: Сотрудник в состоянии выгорания
    psych_status_3 = UserPsychStatus(
        date=datetime(2024, 1, 5),
        summary="Выявлены признаки профессионального выгорания. Снижена продуктивность, наблюдается эмоциональное истощение. Сотрудник испытывает трудности с концентрацией.",
        recommendations="Срочно организовать консультацию с психологом. Предоставить дополнительные дни отдыха. Временно снизить нагрузку. Рассмотреть возможность ротации задач.",
        status=["выгорание", "эмоциональное истощение", "сниженная продуктивность", "тревожность",
                "требуется немедленная помощь"]
    )

    example_psych_statuses = [
        psych_status_1, psych_status_2, psych_status_3
    ]

    query_system = QuerySystem()
    query_system.query(QueryRequest(example_psych_statuses))