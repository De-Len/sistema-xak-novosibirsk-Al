import asyncio
from typing import Any, List, Tuple

import torch  # ✅ Правильный импорт PyTorch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from config import Config
from src.core.interfaces.IEmotionalClassification import IEmotionalClassification
from src.infrastructure.async_decorator.run_in_executor import run_in_executor


class EmotionalClassification(IEmotionalClassification):
    def __init__(self):
        self.config = Config()
        self.model_name = self.config.EMOTIONAL_CLASSIFICATION_MODEL_NAME
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
        self.model.eval()  # ✅ Важно перевести модель в режим оценки

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

    @run_in_executor
    def _extract_emotion_sync(self, message: str) -> List[Tuple[str, float]]:
        """Синхронная версия метода (запускается в отдельном потоке)"""
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

        return sorted(emotion_scores.items(), key=lambda x: x[1], reverse=True)

    async def extract_emotion(self, message: str) -> List[Tuple[str, float]]:
        """Асинхронный интерфейс для анализа эмоций"""
        return await self._extract_emotion_sync(message)

    async def extract_emotion_batch(self, messages: List[str]) -> List[List[Tuple[str, float]]]:
        """Параллельная обработка батча сообщений"""
        tasks = [self.extract_emotion(msg) for msg in messages]
        return await asyncio.gather(*tasks)