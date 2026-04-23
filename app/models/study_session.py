from sqlalchemy import Integer, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.models.base import Base


class StudySession(Base):
    __tablename__ = "study_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    plan_id: Mapped[int] = mapped_column(ForeignKey("plans.id"), nullable=False)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"), nullable=False)

    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    duration: Mapped[int] = mapped_column(Integer, nullable=False)  # minutes
    status: Mapped[str] = mapped_column(String(20), default="pending")

    # Relationships
    plan = relationship("Plan", back_populates="sessions")
    subject = relationship("Subject", back_populates="sessions")
    progress = relationship("Progress", back_populates="session", uselist=False)