from dataclasses import dataclass
from typing import List, Dict, Any
import json


@dataclass
class BurnoutResult:
    emotional_exhaustion: int
    depersonalization: int
    reduction_of_achievements: int
    burnout_index: float
    recommendations: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Возвращает в точности оригинальный формат"""
        return {
            "emotional_exhaustion": self.emotional_exhaustion,
            "depersonalization": self.depersonalization,
            "reduction_of_achievements": self.reduction_of_achievements,
            "burnout_index": self.burnout_index,
            "recommendations": self.recommendations
        }

    def to_json(self) -> str:
        """Возвращает JSON строку в оригинальном формате"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)