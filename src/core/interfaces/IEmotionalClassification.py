from abc import ABC, abstractmethod
from typing import List


class IEmotionalClassification(ABC):
    @abstractmethod
    def extract_emotions(self, user_messages: List[str]) -> List[float]:
        pass