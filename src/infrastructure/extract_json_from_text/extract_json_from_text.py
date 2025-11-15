import re
import json


def extract_json_from_text(text) -> str:
    """
    Извлекает JSON строку из текста, находя содержимое между ```json и ```

    Args:
        text (str): Исходный текст

    Returns:
        dict or list: Распарсенный JSON объект или None если не найден
    """
    # Паттерн для поиска содержимого между ```json и ```
    pattern = r'```json\s*(.*?)\s*```'

    # Ищем все совпадения
    matches = re.findall(pattern, text, re.DOTALL)

    if matches:
        # Берем первое совпадение
        json_string = matches[0]
        try:
            # Парсим JSON
            return json_string
        except json.JSONDecodeError as e:
            print(f"Ошибка парсинга JSON: {e}")
            return None
    else:
        print("JSON не найден в тексте")
        return None


# Пример использования
if __name__ == "__main__":

    data = """
    TESTTEST
    ```json
    {
      "emotional_exhaustion": 16,
      "depersonalization": 6,
      "reduction_of_achievements": 31,
      "burnout_index": 0.40,
      "recommendations": [
        "Практикуйте короткие перерывы в течение дня для восстановления энергии.",
        "Попробуйте техники осознанного общения, чтобы снизить дистанцию с коллегами.",
        "Разнообразьте задачи или обсудите с руководителем возможность ротации обязанностей.",
        "Составьте график с четкими границами работы и отдыха, сохраняя хобби как обязательный пункт."
      ]
    }
    ```
    TESTTEST
    """

    print(extract_json_from_text(data))