import json
import re
from typing import Optional, Dict, Any, List

from src.core.entities.BurnoutResultEntities import BurnoutResult


class BurnoutAnalysisParser:
    """
    Парсер для извлечения JSON из ответов LLM.
    Поддерживает произвольный текст, markdown, вложенные JSON-объекты,
    автоматическую коррекцию типичных ошибок и валидирует структуру.
    """

    @staticmethod
    def parse_from_json(text: str) -> Optional[BurnoutResult]:
        """
        Извлекает JSON, исправляет ошибки, валидирует поля
        и возвращает объект BurnoutResult.
        """

        json_str = BurnoutAnalysisParser._extract_json_from_text(text)

        if not json_str:
            print("❌ JSON не найден в тексте")
            return None

        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            print("❌ JSON повреждён и не может быть прочитан:", e)
            print("JSON:", json_str[:200])
            return None

        try:
            BurnoutAnalysisParser._validate_fields(data)
            BurnoutAnalysisParser._validate_ranges(data)
        except ValueError as e:
            print("❌ Ошибка валидации:", e)
            return None

        return BurnoutResult(
            emotional_exhaustion=data["emotional_exhaustion"],
            depersonalization=data["depersonalization"],
            reduction_of_achievements=data["reduction_of_achievements"],
            burnout_index=float(data["burnout_index"]),
            recommendations=data["recommendations"],
        )

    @staticmethod
    def _extract_json_from_text(text: str) -> Optional[str]:
        """
        Извлекает JSON объект по уровням вложенности.
        Убирает markdown-код, форматирование, лишний текст.
        """

        # Удаляем markdown ```...``` блоки
        text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)

        stack = 0
        json_start = None
        candidates = []

        for i, ch in enumerate(text):
            if ch == '{':
                if stack == 0:
                    json_start = i
                stack += 1
            elif ch == '}':
                if stack > 0:
                    stack -= 1
                if stack == 0 and json_start is not None:
                    candidates.append(text[json_start:i + 1])
                    json_start = None

        if not candidates:
            return None

        # Сортируем по длине: самый большой — вероятнее правильный
        candidates = sorted(candidates, key=len, reverse=True)

        for candidate in candidates:
            c = candidate.strip()
            if BurnoutAnalysisParser._is_valid_json(c):
                return c

            fixed = BurnoutAnalysisParser._fix_common_json_errors(c)
            if fixed and BurnoutAnalysisParser._is_valid_json(fixed):
                return fixed

        return None

    @staticmethod
    def _fix_common_json_errors(s: str) -> Optional[str]:
        """
        Чинит типичные ошибки:
        - одинарные кавычки → двойные
        - ключи без кавычек → добавляем кавычки
        - висячие запятые
        """

        original = s

        # Одинарные кавычки → двойные
        if "'" in s and '"' not in s:
            s = s.replace("'", '"')

        # Ключи без кавычек {"key":} — иногда LLM пишет key: "value"
        s = re.sub(r'(\s*)([A-Za-z_]\w*)\s*:', r'\1"\2":', s)

        # Удаляем висячие запятые
        s = re.sub(r',\s*}', '}', s)
        s = re.sub(r',\s*]', ']', s)

        try:
            json.loads(s)
            return s
        except:
            return original if BurnoutAnalysisParser._is_valid_json(original) else None

    @staticmethod
    def _is_valid_json(s: str) -> bool:
        try:
            json.loads(s)
            return True
        except:
            return False

    @staticmethod
    def _validate_fields(data: Dict[str, Any]):
        """Проверяет наличие и типы обязательных полей"""

        required = [
            "emotional_exhaustion",
            "depersonalization",
            "reduction_of_achievements",
            "burnout_index",
            "recommendations",
        ]

        for field in required:
            if field not in data:
                raise ValueError(f"Отсутствует обязательное поле: {field}")

        # Типы
        if not isinstance(data["emotional_exhaustion"], int):
            raise ValueError("emotional_exhaustion должен быть int")

        if not isinstance(data["depersonalization"], int):
            raise ValueError("depersonalization должен быть int")

        if not isinstance(data["reduction_of_achievements"], int):
            raise ValueError("reduction_of_achievements должен быть int")

        if not isinstance(data["burnout_index"], (float, int)):
            raise ValueError("burnout_index должен быть числом")

        if not isinstance(data["recommendations"], list):
            raise ValueError("recommendations должен быть списком")

        if len(data["recommendations"]) != 4:
            raise ValueError("recommendations должен содержать ровно 4 строки")

        for rec in data["recommendations"]:
            if not isinstance(rec, str):
                raise ValueError("Каждая рекомендация должна быть строкой")

    @staticmethod
    def _validate_ranges(data: Dict[str, Any]):
        """Валидирует диапазоны по методике MBI"""

        ee = data["emotional_exhaustion"]
        dp = data["depersonalization"]
        ra = data["reduction_of_achievements"]
        bi = data["burnout_index"]

        if not (0 <= ee <= 54):
            raise ValueError(f"emotional_exhaustion должен быть 0–54 (получено {ee})")

        if not (0 <= dp <= 30):
            raise ValueError(f"depersonalization должен быть 0–30 (получено {dp})")

        if not (0 <= ra <= 48):
            raise ValueError(f"reduction_of_achievements должен быть 0–48 (получено {ra})")

        if not (0.0 <= bi <= 1.0):
            raise ValueError(f"burnout_index должен быть 0.0–1.0 (получено {bi})")