from abc import ABC, abstractmethod
from typing import AsyncGenerator


class ILLMProvider(ABC):
    @abstractmethod
    async def generate_response(self, messages: list) -> str:
        pass

    @abstractmethod
    async def generate_response_stream(self, messages: list) -> AsyncGenerator[str, None]:
        pass