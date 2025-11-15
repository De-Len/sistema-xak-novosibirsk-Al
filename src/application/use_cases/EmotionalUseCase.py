import asyncio
from typing import List
from src.core.entities import EmotionalCoefficient
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

    async def analyze_single_text(self, text: str) -> EmotionalCoefficient:
        emotions = await self.emotional_classification.extract_emotion(text)

        emotion_dict = {field: 0.0 for field in EmotionalCoefficient.__dataclass_fields__}

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


async def main():
    use_case = EmotionalUseCase(emotional_classification=EmotionalClassification())
    await use_case.emotional_classification.extract_emotion("Я люблю мэдкида")

if __name__ == "__main__":
    asyncio.run(main())