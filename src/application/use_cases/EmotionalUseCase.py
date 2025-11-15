import asyncio
from typing import List, Tuple
from src.core.entities.EmotionalCoefficient import EmotionalCoefficient
from src.core.interfaces.IEmotionalClassification import IEmotionalClassification
from src.infrastructure.emotion_classification.EmotionClassification import EmotionalClassification


class EmotionalUseCase:
    def __init__(self, emotional_classification: IEmotionalClassification):
        self.emotional_classification = emotional_classification
        self.main_emotions: List[str] = [
            'нейтрально', 'радость', 'грусть', 'злость',
            'энтузиазм', 'удивление', 'отвращение', 'страх',
            'вина', 'стыд'
        ]

    async def analyze_single_message(self, message: str) -> EmotionalCoefficient:
        emotions = await self.emotional_classification.extract_emotion(message)

        emotion_dict = {
            "neutral": 0.0,
            "joy": 0.0,
            "sadness": 0.0,
            "anger": 0.0,
            "enthusiasm": 0.0,
            "surprise": 0.0,
            "disgust": 0.0,
            "fear": 0.0,
            "guilt": 0.0,
            "shame": 0.0,
        }

        mapping = {
            'нейтрально': 'neutral',
            'радость': 'joy',
            'грусть': 'sadness',
            'злость': 'anger',
            'энтузиазм': 'enthusiasm',
            'удивление': 'surprise',
            'отвращение': 'disgust',
            'страх': 'fear',
            'вина': 'guilt',
            'стыд': 'shame'
        }

        for emotion_name, score in emotions:
            if emotion_name in mapping:
                emotion_dict[mapping[emotion_name]] = score

        return EmotionalCoefficient(**emotion_dict)

    async def analyze_messages_batch(self, messages: List[str]) -> List[EmotionalCoefficient]:
        """Асинхронно обрабатывает массив текстов"""
        tasks = [self.analyze_single_message(text) for text in messages]
        return await asyncio.gather(*tasks)

    async def analyze_messages_batch_top_emotions(self, messages: List[str]) -> List[Tuple[str, float]]:
        """Возвращает для каждого текста только эмоцию с наибольшим значением"""
        coefficients = await self.analyze_messages_batch(messages)
        top_emotions = []
        for coef in coefficients:
            max_emotion = max(coef.__dict__.items(), key=lambda x: x[1])
            top_emotions.append(max_emotion)
        return top_emotions

# async def main():
#     texts = ["Я люблю мэдкида", 'я ненавижу мэдкида']
#     use_case = EmotionalUseCase(emotional_classification=EmotionalClassification())
#
#     top_emotions = await use_case.analyze_messages_batch_top_emotions(texts)
#
#     for text, (emotion, score) in zip(texts, top_emotions):
#         print(f"{text} → {emotion}: {score:.2f}")
#     print()
#
# if __name__ == "__main__":
#     asyncio.run(main())