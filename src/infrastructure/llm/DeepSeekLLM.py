from typing import AsyncGenerator
from openai import AsyncOpenAI
from config import Config
from src.core.interfaces import ILLMProvider


class DeepSeekLLM(ILLMProvider):
    def __init__(self):
        self.config = Config()
        self.client = AsyncOpenAI(
            api_key=self.config.OPENAI_API_KEY,
            base_url=self.config.LLM_BASE_URL,
        )
        self.model = self.config.LLM_MODEL

    async def generate_response(self, messages: list) -> str:
        try:
            chat_completion = await self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            raise LLMError(f"Ошибка при запросе к DeepSeek API: {e}")

    async def generate_response_stream(self, messages: list) -> AsyncGenerator[str, None]:
        """Настоящий streaming от DeepSeek API"""
        try:
            serializable_messages = self._make_messages_serializable(messages)

            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=serializable_messages,
                stream=True,
                max_tokens=1000
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            yield f"⚠️ Ошибка: {str(e)}"

    def _make_messages_serializable(self, messages: list) -> list:
        serializable_messages = []
        for msg in messages:
            serializable_msg = {
                "role": msg["role"],
                "content": msg["content"]
            }
            serializable_messages.append(serializable_msg)
        return serializable_messages


class LLMError(Exception):
    pass
