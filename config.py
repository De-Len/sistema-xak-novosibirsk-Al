import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    API_KEY = os.getenv("API_KEY")

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    LLM_BASE_URL = os.getenv("LLM_BASE_URL")
    LLM_MODEL = os.getenv("LLM_MODEL")

    MONGODB_CONNECTION_STRING = os.getenv("MONGODB_CONNECTION_STRING")
    MONGODB_DATABASE = os.getenv("MONGODB_DATABASE")

    # project_root = str(os.path.dirname(os.path.abspath(__file__)))
    # DATA_DIRECTORY = project_root + "/data"
