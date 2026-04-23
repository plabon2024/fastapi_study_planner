from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ProgressBase(BaseModel):
    session_id: int
    completion_time: datetime


class ProgressCreate(ProgressBase):
    performance_score: Optional[float] = Field(None, ge=0, le=100)


class ProgressResponse(ProgressBase):
    id: int
    performance_score: Optional[float]

    class Config:
        from_attributes = True