from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DialogueEntity(BaseModel):
    id: Optional[int] = None
    user_id: int
    title: str
    created_at: datetime
    updated_at: datetime
    is_active: bool = True


class MessageEntity(BaseModel):
    id: Optional[int] = None
    dialogue_id: int
    role: str  # 'system', 'user', 'assistant'
    content: str
    timestamp: datetime
    tokens_used: Optional[int] = None