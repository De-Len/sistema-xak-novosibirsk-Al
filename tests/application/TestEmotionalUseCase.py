import pytest
from unittest.mock import Mock, AsyncMock

from src.application.use_cases.EmotionalUseCase import EmotionalUseCase
from src.core.entities.EmotionalCoefficient import EmotionalCoefficient
from src.core.interfaces.IEmotionalClassification import IEmotionalClassification

class TestEmotionalUseCase:

    @pytest.fixture
    def mock_classifier(self):
        return Mock(spec=IEmotionalClassification)

    @pytest.fixture
    def use_case(self, mock_classifier):
        return EmotionalUseCase(emotional_classification=mock_classifier)

    @pytest.mark.asyncio
    async def test_analyze_single_message_success(self, use_case, mock_classifier):
        # Arrange
        test_message = "Я очень рад этому"
        mock_emotions = [('радость', 0.8), ('нейтрально', 0.2)]
        mock_classifier.extract_emotion = AsyncMock(return_value=mock_emotions)

        result = await use_case.analyze_single_message(test_message)

        assert isinstance(result, EmotionalCoefficient)
        assert result.joy == 0.8
        assert result.neutral == 0.2
        assert result.sadness == 0.0
        mock_classifier.extract_emotion.assert_called_once_with(test_message)

    @pytest.mark.asyncio
    async def test_analyze_single_message_unknown_emotion(self, use_case, mock_classifier):
        test_message = "Неизвестная эмоция"
        mock_emotions = [('неизвестная', 0.9), ('радость', 0.1)]
        mock_classifier.extract_emotion = AsyncMock(return_value=mock_emotions)

        result = await use_case.analyze_single_message(test_message)

        assert result.joy == 0.1
        assert result.neutral == 0.0

    @pytest.mark.asyncio
    async def test_analyze_messages_batch(self, use_case, mock_classifier):
        messages = ["Сообщение 1", "Сообщение 2"]
        mock_emotions_1 = [('радость', 0.7)]
        mock_emotions_2 = [('грусть', 0.6)]
        mock_classifier.extract_emotion = AsyncMock(side_effect=[mock_emotions_1, mock_emotions_2])

        results = await use_case.analyze_messages_batch(messages)

        assert len(results) == 2
        assert results[0].joy == 0.7
        assert results[1].sadness == 0.6
        assert mock_classifier.extract_emotion.call_count == 2

    @pytest.mark.asyncio
    async def test_analyze_messages_batch_top_emotions(self, use_case, mock_classifier):
        messages = ["Радостное", "Грустное"]
        mock_emotions_1 = [('радость', 0.9), ('нейтрально', 0.1)]
        mock_emotions_2 = [('грусть', 0.8), ('радость', 0.2)]
        mock_classifier.extract_emotion = AsyncMock(side_effect=[mock_emotions_1, mock_emotions_2])

        results = await use_case.analyze_messages_batch_top_emotions(messages)

        assert len(results) == 2
        assert results[0] == ('joy', 0.9)
        assert results[1] == ('sadness', 0.8)

    @pytest.mark.asyncio
    async def test_analyze_empty_messages_batch(self, use_case, mock_classifier):
        messages = []

        results = await use_case.analyze_messages_batch(messages)

        assert len(results) == 0
        mock_classifier.extract_emotion.assert_not_called()

    @pytest.mark.asyncio
    async def test_emotion_mapping_completeness(self, use_case):
        for russian_emotion in use_case.main_emotions:
            assert russian_emotion in use_case.main_emotions