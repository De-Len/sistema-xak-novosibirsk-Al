import re
import json


def extract_json_from_text(text) -> str | None:
    pattern = r'```json\s*(.*?)\s*```'
    matches = re.findall(pattern, text, re.DOTALL)

    if not matches:
        return None

    json_string = matches[0]

    try:
        json.loads(json_string)  # проверка JSON корректности
    except json.JSONDecodeError:
        return None

    return json_string


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