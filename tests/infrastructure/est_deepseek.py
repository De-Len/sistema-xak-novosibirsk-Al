import asyncio
from openai import AsyncOpenAI
from config import Config

config = Config()

client = AsyncOpenAI(
    api_key=config.OPENAI_API_KEY,
    base_url=config.DEEPSEEK_BASE_URL,
)

system_prompt = ("""
Ты профессиональный психолог, проводящий опрос по методике выгорания Маслач (MBI). 
Твоя задача:

1. Задай мне 8 вопросов о моем эмоциональном состоянии и профессиональном выгорании
2. Задавай вопросы ПО ОДНОМУ - сначала задай вопрос, дождись моего ответа, потом следующий вопрос
3. Вопросы должны быть развернутыми, побуждающими к рефлексии, а не как в тесте с вариантами ответов
4. После получения всех 8 ответов - проанализируй их и дай развернутые результаты по трем шкалам:
   - Эмоциональное истощение
   - Деперсонализация  
   - Редукция профессиональных достижений
5. Также дай персональные рекомендации

Не торопись, веди диалог естественно и поддерживающе.
""")

# Инициализируем историю сообщений
messages = [
    {
        "role": "system",
        "content": system_prompt
    }
]


async def get_assistant_response():
    """Асинхронно получает ответ от ассистента"""
    try:
        chat_completion = await client.chat.completions.create(
            model="deepseek/deepseek-chat-v3-0324",
            messages=messages
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Произошла ошибка при запросе к API: {e}")
        return None


async def async_input(prompt: str) -> str:
    """Асинхронный ввод от пользователя"""
    return await asyncio.get_event_loop().run_in_executor(None, input, prompt)


async def start_burnout_survey():
    """Запускает опрос и получает первый вопрос"""
    global messages

    print("=" * 60)
    print("ОПРОС ПРОФЕССИОНАЛЬНОГО ВЫГОРАНИЯ (MBI)")
    print("=" * 60)
    print("Я задам вам 8 вопросов о вашем эмоциональном состоянии.")
    print("Отвечайте развернуто, как вам comfortable.")
    print("Для выхода введите 'выход'")
    print("=" * 60)
    print()

    # Первый запрос к ассистенту, чтобы он начал опрос
    starter_message = "Начни опрос профессионального выгорания. Задай первый вопрос."
    messages.append({"role": "user", "content": starter_message})

    # Получаем первый вопрос от ассистента
    assistant_response = await get_assistant_response()

    if assistant_response:
        messages.append({"role": "assistant", "content": assistant_response})
        print(f"Ассистент: {assistant_response}")
        return True
    else:
        print("Не удалось начать опрос. Попробуйте позже.")
        return False

async def chat_with_limited_history(max_messages=20):
    """Асинхронная версия с ограничением истории"""
    global messages

    print("=" * 60)
    print("ОПРОС ПРОФЕССИОНАЛЬНОГО ВЫГОРАНИЯ (с ограниченной историей)")
    print("=" * 60)

    # Запускаем опрос
    if not await start_burnout_survey():
        return

    question_count = 1
    max_questions = 8

    while question_count <= max_questions:
        print(f"\n[Вопрос {question_count}/{max_questions}]")

        # Асинхронно получаем ответ пользователя
        user_input = await async_input("Ваш ответ: ")
        user_input = user_input.strip()

        if user_input.lower() in ['выход', 'exit', 'quit']:
            print("\nОпрос прерван. До свидания!")
            return

        if not user_input:
            print("Пожалуйста, введите ответ.")
            continue

        # Добавляем сообщение пользователя
        messages.append({"role": "user", "content": user_input})

        # Ограничиваем размер истории
        if len(messages) > max_messages + 1:
            messages = [messages[0]] + messages[-(max_messages - 1):]

        # Показываем индикатор загрузки
        print("Ассистент думает...", end="", flush=True)

        # Асинхронно получаем ответ
        assistant_response = await get_assistant_response()

        if assistant_response:
            messages.append({"role": "assistant", "content": assistant_response})
            print("\r" + " " * 30 + "\r")  # Очищаем строку с индикатором
            print(f"Ассистент: {assistant_response}")

            question_count += 1

            if any(word in assistant_response.lower() for word in
                   ['результат', 'итог', 'анализ', 'рекомендац', 'заключен']):
                print("\n" + "=" * 60)
                print("ОПРОС ЗАВЕРШЕН!")
                print("=" * 60)
                break
        else:
            print("\nНе удалось получить ответ от ассистента. Попробуйте еще раз.")


async def main():
    """Основная асинхронная функция"""

    await chat_with_limited_history(max_messages=15)


# Запускаем асинхронное приложение
if __name__ == "__main__":
    asyncio.run(main())