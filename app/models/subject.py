from sqlalchemy import Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.models.base import Base


class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    difficulty: Mapped[int] = mapped_column(Integer, nullable=False)
    estimated_hours: Mapped[float] = mapped_column(Float, nullable=False)
    exam_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Relationships
    user = relationship("User", back_populates="subjects")
    sessions = relationship("StudySession", back_populates="subject")