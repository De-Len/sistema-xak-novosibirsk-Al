import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # API
    API_KEY = os.getenv("API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.proxyapi.ru/openrouter/v1")

    MONGODB_CONNECTION_STRING: str = "mongodb://localhost:27017"  # или ваш connection string
    MONGODB_DATABASE: str = "burnout_survey"

    LLM_MODEL = os.getenv("LLM_MODEL")

    # Data
    project_root = str(os.path.dirname(os.path.abspath(__file__)))
    # DATA_DIRECTORY = os.getenv("DATA_DIRECTORY", project_root + "/data")
    DATA_DIRECTORY = project_root + "/data"
