import pytest
from src.infrastructure.emotion_classification.EmotionClassification import EmotionalClassification


@pytest.mark.asyncio
async def test_emotion_classification():
    emotional_classification = EmotionalClassification()

    test_texts = [
        "Получил пятерку за экзамен! Я на седьмом небе от счастья!",
        "Мой друг переезжает в другой город, мне так грустно...",
        "Темно и страшно, кажется, кто-то есть в доме...",
        "Этот человек постоянно меня раздражает!",
        "Невероятно! Ты выиграл в лотерею!"
    ]

    print("\n=== ДЕТАЛЬНЫЙ АНАЛИЗ ЭМОЦИЙ ===\n")

    for text in test_texts:
        emotions = await emotional_classification.extract_emotion(text)

        print(f"📝 Текст: \"{text}\"")
        print("📊 Распределение эмоций:")

        for emotion, score in emotions:
            print(f"   {emotion}: {score:.3f}")

        main_emotion, main_score = emotions[0]
        print(f"🎯 Основная эмоция: {main_emotion} ({main_score:.3f})")
        print("─" * 70)


@pytest.mark.asyncio
async def test_batch_processing():
    emotional_classification = EmotionalClassification()

    test_texts = [
        "Я очень рад!",
        "Мне грустно...",
        "Боюсь завтрашнего дня"
    ]

    results = await emotional_classification.extract_emotion_batch(test_texts)

    assert len(results) == len(test_texts)

    for emotion_list in results:
        assert isinstance(emotion_list, list)
        for emotion, score in emotion_list:
            assert isinstance(emotion, str)
            assert isinstance(score, float)
            assert 0 <= score <= 1


@pytest.mark.asyncio
async def test_single_emotion():
    emotional_classification = EmotionalClassification()

    text = "Я очень счастлив!"
    emotions = await emotional_classification.extract_emotion(text)

    assert len(emotions) > 0

    # Проверяем, что самая высокая оценка не превышает 1
    assert emotions[0][1] <= 1.0

    scores = [score for _, score in emotions]
    assert scores == sorted(scores, reverse=True)