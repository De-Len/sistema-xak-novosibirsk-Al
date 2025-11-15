from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel
from src.core.entities.user_entites.Department import Department
from src.core.entities.user_entites.Gender import Gender

class UserEntity(BaseModel):
    id: Optional[int] = None
    full_name: str
    legal_entity: str
    gender: Gender
    city: str
    position: str
    experience: float
    age: int
    subordinates_count: int
    department: Department

    performance_metrics: Dict[str, float]

    certification_passed: Optional[bool] = None
    training_completed: bool
    last_vacation: Optional[datetime] = None
    sick_leave_2025: bool
    has_reprimand: bool
    corporate_activities_participation: bool

    surveys_per_week: int = 2
    survey_complexity: str = "standard"



