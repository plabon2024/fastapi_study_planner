from pydantic import BaseModel
from datetime import datetime
from typing import List


class PlannerSubjectInput(BaseModel):
    subject_id: int


class PlanGenerateRequest(BaseModel):
    subjects: List[PlannerSubjectInput]
    daily_available_hours: float
    start_date: datetime