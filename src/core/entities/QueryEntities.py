# src/core/entities/QueryEntities.py
from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Union

from src.core.entities.BurnoutResults import BurnoutResult
from src.core.entities.UserEntities import ListUserPsychStatus


@dataclass
class Document:
    content: str
    metadata: Dict[str, Any]
    id: Optional[str] = None


@dataclass
class QueryResult:
    query: str
    documents: List[Document]
    similarity_scores: List[float]


@dataclass
class VectorSearchResult:
    document: Document
    similarity_score: float


@dataclass
class QueryRequest:
    user_input: str = ""
    chat_id: Optional[str] = None
    max_questions: int = 8
    max_history_messages: int = 20
    list_user_psych_status: Optional[ListUserPsychStatus] = None


@dataclass
class LLMResponse:
    content: Union[str, BurnoutResult]  # текст или результат анализа
    chat_id: str
    is_completed: bool
    question_count: int
    total_questions: int
    is_analysis: bool = False


@dataclass
class LLMStreamResponse:
    content_chunk: str
    chat_id: str
    is_completed: bool
    question_count: int
    total_questions: int
    is_final_chunk: bool = False
    is_analysis: bool = False

