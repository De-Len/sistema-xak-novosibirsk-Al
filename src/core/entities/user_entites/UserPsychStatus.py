import asyncio
from datetime import datetime
from typing import List
from openai import BaseModel


class UserPsychStatus(BaseModel):
    date: datetime = None
    summary: str
    recommendations: str
    status: List[float]

    async def _format_date(self) -> str:
        """Асинхронно форматирует дату"""
        if not self.date:
            return "Не указана"
        await asyncio.sleep(0.001)
        return self.date.strftime("%d.%m.%Y в %H:%M")

    async def _analyze_status_components(self) -> str:
        """Асинхронно анализирует компоненты статуса"""
        if len(self.status) != 4:
            return "   Ошибка: должно быть 4 показателя\n"

        emotional_exhaustion, depersonalization, reduction, burnout_index = self.status

        analysis_lines = [f"   1. Эмоциональное истощение: {emotional_exhaustion} ({str(self.status[0])})",
                          f"   2. Деперсонализация: {depersonalization} ({str(self.status[1])})",
                          f"   3. Редукция проф. достижений: {reduction} ({str(self.status[2])})"
                          f"   4. Системный индекс синдрома перегорания: {burnout_index} ({str(self.status[3])})"]


        return "\n".join(analysis_lines) + "\n"

    async def to_string(self) -> str:
        """
        Асинхронно преобразует все параметры в читаемую строку.
        """
        # Форматируем дату
        date_str = await self._format_date()

        # Анализируем статус
        status_analysis = await self._analyze_status_components()

        result = (
            "📊 ПСИХОЛОГИЧЕСКИЙ СТАТУС\n"
            "────────────────────\n"
            f"📅 Дата оценки: {date_str}\n"
            f"📋 Сводка: {self.summary}\n"
            f"💡 Рекомендации: {self.recommendations}\n"
            f"📈 Показатели:\n{status_analysis}"
            "────────────────────"
        )

        return result