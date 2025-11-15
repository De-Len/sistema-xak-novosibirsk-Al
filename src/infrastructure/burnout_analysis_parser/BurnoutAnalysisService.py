from typing import Optional

from src.core.entities.BurnoutResultEntities import BurnoutResult
from src.infrastructure.burnout_analysis_parser.BurnoutAnalysisParser import BurnoutAnalysisParser


class BurnoutAnalysisService:
    def __init__(self):
        self.parser = BurnoutAnalysisParser()

    def parse_llm_response(self, llm_response: str) -> Optional[BurnoutResult]:
        """Парсит ответ от LLM в объект BurnoutResult"""
        return self.parser.parse_from_json(llm_response)

    def validate_result(self, result: BurnoutResult) -> bool:
        """Проверяет валидность результата"""
        try:
            # Проверяем диапазоны
            if not (0 <= result.emotional_exhaustion <= 54):
                return False
            if not (0 <= result.depersonalization <= 30):
                return False
            if not (0 <= result.reduction_of_achievements <= 48):
                return False
            if not (0.0 <= result.burnout_index <= 1.0):
                return False
            if len(result.recommendations) != 4:
                return False

            return True
        except:
            return False

    def get_result_summary(self, result: BurnoutResult) -> str:
        """Возвращает текстовую сводку результата"""
        return f"""
Результаты анализа выгорания:
- Эмоциональное истощение: {result.emotional_exhaustion}/54
- Деперсонализация: {result.depersonalization}/30
- Редукция достижений: {result.reduction_of_achievements}/48
- Индекс выгорания: {result.burnout_index:.3f}
"""

    def save_result_to_file(self, result: BurnoutResult, filename: str):
        """Сохраняет результат в файл"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(result.to_json())