from datetime import datetime
from enum import Enum
from typing import Optional, Dict
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
    status: []