from dataclasses import dataclass
from typing import List


@dataclass
class BurnoutResult:
    emotional_exhaustion: int
    depersonalization: int
    reduction_of_achievements: int
    burnout_index: float
    recommendations: List[str]