from abc import ABC, abstractmethod
from typing import Any


class IEmotionalClassification(ABC):
    @abstractmethod
    def extract_emotion(self, message: str) -> list[tuple[str | Any, Any]]:
        pass