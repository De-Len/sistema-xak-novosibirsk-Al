import asyncio
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, List
from pydantic import BaseModel


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"


class Department(str, Enum):
    HR = "hr"
    IT = "it"
    SALES = "sales"
    SUPPORT = "support"
    MANAGEMENT = "management"


class UserEntity(BaseModel):
    id: Optional[int] = None
    full_name: str
    legal_entity: str
    gender: Gender
    city: str
    position: str
    experience: float  # years
    age: int
    subordinates_count: int
    department: Department

    # Monthly performance metrics
    performance_metrics: Dict[str, float]  # june, july, etc.

    # Additional factors
    certification_passed: Optional[bool] = None
    training_completed: bool
    last_vacation: Optional[datetime] = None
    sick_leave_2025: bool
    has_reprimand: bool
    corporate_activities_participation: bool

    # Survey settings
    surveys_per_week: int = 2
    survey_complexity: str = "standard"

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

class ListUserPsychStatus(BaseModel):
    list_user_psych_status: List[UserPsychStatus]
    user_id: int

    async def to_string(self) -> str:
        """Объединяет все статусы в одну строку"""
        if not self.list_user_psych_status:
            return "📭 Нет данных о психологических статусах"

        tasks = [status.to_string() for status in self.list_user_psych_status]
        status_strings = await asyncio.gather(*tasks)

        result_parts = [
            f"📊 Психологические статусы пользователя {self.user_id}",
            f"📋 Количество записей: {len(self.list_user_psych_status)}",
            "=" * 50
        ]

        for i, status_str in enumerate(status_strings, 1):
            result_parts.append(f"📄 ЗАПИСЬ #{i}")
            result_parts.append(status_str)
            if i < len(status_strings):
                result_parts.append("─" * 40)

        return "\n".join(result_parts)