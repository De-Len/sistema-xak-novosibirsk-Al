from typing import Optional
from openai import OpenAI
from src.core.entities import LLMResponse
from src.core.interfaces import ILLMProvider
import asyncio


class DeepSeekLLM(ILLMProvider):
    def __init__(self, api_key: str, base_url: str = "https://api.proxyapi.ru/openrouter/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.model_name = "deepseek/deepseek-chat-v3-0324"

        # Инициализируем OpenAI клиент once
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def _sync_generate(self, full_prompt: str) -> LLMResponse:
        result = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": full_prompt}]
        )
        return LLMResponse(
            content=result.choices[0].message.content,
            prompt_tokens=result.usage.prompt_tokens,
            completion_tokens=result.usage.completion_tokens,
            total_tokens=result.usage.total_tokens
        )

    async def generate_response(self, prompt: str, context: Optional[str] = None) -> LLMResponse:
        full_prompt = self._build_prompt(prompt, context)
        # оборачиваем sync вызов в отдельный поток
        result = await asyncio.to_thread(self._sync_generate, full_prompt)
        return result

    def _build_prompt(self, prompt: str, context: Optional[str] = None) -> str:
        if context:
            return f"""Контекст:
                    {context}
                    
                    Запрос: {prompt}
                    
                    Ответь на запрос используя предоставленный контекст.
                    Не используй форматирование (кроме переносов строки).
                    Представь, что ты ассистент, не говори посторонней информации."""
        else:
            return prompt

    def get_model_name(self) -> str:
        return self.model_name