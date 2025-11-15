from typing import List

from src.core.interfaces.IEmotionalClassification import IEmotionalClassification
from src.infrastructure.emotion_classification.EmotionClassification import EmotionalClassification


class EmotionalUseCase:
    def __init__(self, emotional_classification: IEmotionalClassification):
        self.emotional_classification = EmotionalClassification
        self.main_emotions: List[str]
