from sqlalchemy import Integer, DateTime, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.models.base import Base


class Progress(Base):
    __tablename__ = "progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    session_id: Mapped[int] = mapped_column(ForeignKey("study_sessions.id"), nullable=False)

    completion_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    performance_score: Mapped[float] = mapped_column(Float, nullable=True)

    # Relationships
    session = relationship("StudySession", back_populates="progress")