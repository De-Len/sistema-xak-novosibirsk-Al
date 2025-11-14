import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # API
    API_KEY = os.getenv("API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.proxyapi.ru/openrouter/v1")

    # Vector Store
    VECTOR_STORE_PATH = os.getenv("VECTOR_STORE_PATH", "./chroma_db")

    # Data
    project_root = str(os.path.dirname(os.path.abspath(__file__)))
    # DATA_DIRECTORY = os.getenv("DATA_DIRECTORY", project_root + "/data")
    DATA_DIRECTORY = project_root + "/data"


    # Embeddings
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "ai-forever/sbert_large_nlu_ru")