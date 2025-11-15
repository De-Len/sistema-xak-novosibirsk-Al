from typing import Any

from sympy.printing.pytorch import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from config import Config
from src.core.interfaces.IEmotionalClassification import IEmotionalClassification


class EmotionalClassification (IEmotionalClassification):
    def __init__(self):
        self.config = Config()
        self.model_name = self.config.EMOTIONAL_CLASSIFICATION_MODEL_NAME
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)

        self.label_names = {
            'neutral': 'нейтрально',
            'joy': 'радость',
            'sadness': 'грусть',
            'anger': 'злость',
            'enthusiasm': 'энтузиазм',
            'surprise': 'удивление',
            'disgust': 'отвращение',
            'fear': 'страх',
            'guilt': 'вина',
            'shame': 'стыд'
        }
    def extract_emotion(self, message: str) -> list[tuple[str | Any, Any]]:
        """Детальный анализ эмоций с вероятностями для всех классов"""

        inputs = self.tokenizer(
            message,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=512
        )

        with torch.no_grad():
            outputs = self.model(**inputs)

        probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)[0]

        id2label = self.model.config.id2label
        emotion_scores = {}

        for i, prob in enumerate(probabilities):
            label_en = id2label[i]
            label_ru = self.label_names.get(label_en, label_en)
            emotion_scores[label_ru] = prob.item()

        sorted_emotions = sorted(emotion_scores.items(), key=lambda x: x[1], reverse=True)

        return sorted_emotions

