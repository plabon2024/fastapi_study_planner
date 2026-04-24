from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ProgressBase(BaseModel):
    session_id: int


class ProgressCreate(ProgressBase):
    completion_time: Optional[datetime] = None
    performance_score: Optional[float] = Field(None, ge=0, le=100)


class MarkMissedRequest(BaseModel):
    session_id: int


class ProgressResponse(ProgressBase):
    id: int
    completion_time: datetime
    performance_score: Optional[float]

    class Config:
        from_attributes = True