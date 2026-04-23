from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class PlanBase(BaseModel):
    start_date: datetime
    end_date: datetime


class PlanCreate(PlanBase):
    pass


class PlanUpdate(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[str] = None


class PlanResponse(PlanBase):
    id: int
    user_id: int
    created_at: datetime
    total_hours: float
    status: str  

    class Config:
        from_attributes = True