from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

from .enums import SessionStatus
class StudySessionBase(BaseModel):
    subject_id: int
    date: datetime
    duration: int = Field(..., gt=0)  


class StudySessionCreate(StudySessionBase):
    plan_id: int


class StudySessionUpdate(BaseModel):
    date: Optional[datetime] = None
    duration: Optional[int] = Field(None, gt=0)
    status: Optional[str] = None


class StudySessionResponse(StudySessionBase):
    id: int
    plan_id: int
    status:  SessionStatus # pending / completed / missed

    class Config:
        from_attributes = True