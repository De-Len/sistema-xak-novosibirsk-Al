import sys
import os

from src.application.use_cases.BuildVectorStoreUseCase import BuildVectorStoreUseCase
from src.application.use_cases.QueryLLMUseCase import QueryLLMUseCase
from src.core.entities import QueryRequest, LLMResponse
from src.infrastructure.file_reader.FileReader import FileReader
from src.infrastructure.llm.DeepSeekLLM import DeepSeekLLM
from src.infrastructure.vector_store.ChromaVectorStore import ChromaVectorStore

sys.path.append(os.path.dirname(os.path.dirname(__file__)))


from config import Config


class RAGApplication:
    def __init__(self, config: Config):
        self.config = config

        # Инициализация зависимостей
        self.file_reader = FileReader()
        self.vector_store = ChromaVectorStore(
            persist_directory=config.VECTOR_STORE_PATH
        )
        self.llm_provider = DeepSeekLLM(
            api_key=config.OPENAI_API_KEY,
            base_url=config.DEEPSEEK_BASE_URL
        )

        # Инициализация use cases
        self.build_vector_store_uc = BuildVectorStoreUseCase(
            self.file_reader, self.vector_store
        )
        self.query_llm_uc = QueryLLMUseCase(
            self.vector_store, self.llm_provider
        )

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
        self.rag_app = RAGApplication(Config())
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
    query_system = QuerySystem()
    query_system.query(QueryRequest("Подскажите, а где находится дирекция?"))