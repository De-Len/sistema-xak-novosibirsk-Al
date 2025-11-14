from openai import AsyncOpenAI
from config import Config
from src.core.interfaces import ILLMProvider


class DeepSeekLLM(ILLMProvider):
    def __init__(self):
        self.config = Config()
        self.client = AsyncOpenAI(
            api_key=self.config.OPENAI_API_KEY,
            base_url=self.config.DEEPSEEK_BASE_URL,
        )
        self.model = "deepseek/deepseek-chat-v3-0324"

    async def generate_response(self, messages: list) -> str:
        try:
            chat_completion = await self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            raise LLMError(f"Ошибка при запросе к DeepSeek API: {e}")


class LLMError(Exception):
    pass
