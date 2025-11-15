import asyncio
from typing import List
from openai import BaseModel
from src.core.entities.user_entites.UserPsychStatus import UserPsychStatus


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