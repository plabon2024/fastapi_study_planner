from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class SubjectBase(BaseModel):
    name: str = Field(..., max_length=100)
    difficulty: int = Field(..., ge=1, le=5)
    estimated_hours: float = Field(..., gt=0)
    exam_date: datetime


class SubjectCreate(SubjectBase):
    pass


class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    difficulty: Optional[int] = Field(None, ge=1, le=5)
    estimated_hours: Optional[float] = Field(None, gt=0)
    exam_date: Optional[datetime] = None


class SubjectResponse(SubjectBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
