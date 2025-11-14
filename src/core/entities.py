from dataclasses import dataclass
from typing import List, Optional, Dict, Any

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
class LLMResponse:
    content: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

@dataclass
class VectorSearchResult:
    document: Document
    similarity_score: float

@dataclass
class QueryRequest:
    question: str
    top_k: Optional[int] = 3