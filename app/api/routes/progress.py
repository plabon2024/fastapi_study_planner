from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated, List
from datetime import datetime

from app.db.session import get_db
from app.models.study_session import StudySession
from app.models.progress import Progress
from app.models.plan import Plan
from app.models.user import User

from app.schemas.progress import ProgressCreate, ProgressResponse, MarkMissedRequest

from app.api.routes.auth import get_current_user


router = APIRouter(tags=["Progress"])


@router.post("/mark-complete", response_model=ProgressResponse)
def mark_complete(
    data: ProgressCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    session = (
        db.query(StudySession)
        .join(Plan)
        .filter(
            StudySession.id == data.session_id,
            Plan.user_id == current_user.id
        )
        .first()
    )

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.status == "completed":
        raise HTTPException(status_code=400, detail="Session already completed")

    if session.status == "missed":
        raise HTTPException(status_code=400, detail="Cannot complete a missed session")

    existing = db.query(Progress).filter(
        Progress.session_id == session.id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Progress already exists")

    try:
        session.status = "completed"

        progress = Progress(
            session_id=session.id,
            completion_time=data.completion_time or datetime.utcnow(),
            performance_score=data.performance_score
        )

        db.add(progress)
        db.commit()
        db.refresh(progress)

        return progress

    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to mark complete")

@router.post("/mark-missed", response_model=dict)
def mark_missed(
    data: MarkMissedRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    session = (
        db.query(StudySession)
        .join(Plan)
        .filter(
            StudySession.id == data.session_id,
            Plan.user_id == current_user.id
        )
        .first()
    )

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.status == "completed":
        raise HTTPException(status_code=400, detail="Cannot mark completed session as missed")

    session.status = "missed"

    try:
        db.commit()
        return {"message": "Session marked as missed"}
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update session")

@router.get("/{plan_id}", response_model=List[ProgressResponse])
def get_progress(
    plan_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    plan = db.query(Plan).filter(
        Plan.id == plan_id,
        Plan.user_id == current_user.id
    ).first()

    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    return (
        db.query(Progress)
        .join(StudySession)
        .filter(StudySession.plan_id == plan_id)
        .all()
    )


@router.get("/{plan_id}/stats")
def get_progress_stats(
    plan_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    plan = (
        db.query(Plan)
        .filter(Plan.id == plan_id, Plan.user_id == current_user.id)
        .first()
    )

    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    sessions = (
        db.query(StudySession)
        .filter(StudySession.plan_id == plan_id)
        .all()
    )

    total = len(sessions)
    completed = len([s for s in sessions if s.status == "completed"])
    missed = len([s for s in sessions if s.status == "missed"])
    pending = len([s for s in sessions if s.status == "pending"])

    completion_rate = (completed / total * 100) if total > 0 else 0

    return {
        "total_sessions": total,
        "completed": completed,
        "missed": missed,
        "pending": pending,
        "completion_rate": round(completion_rate, 2)
    }












