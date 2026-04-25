from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated, List
from datetime import datetime, date

from app.db.session import get_db
from app.models.study_session import StudySession
from app.models.plan import Plan
from app.models.user import User
from app.models.progress import Progress

from app.schemas.study_session import (
    StudySessionResponse,
    StudySessionUpdate
)

from app.api.routes.auth import get_current_user


router = APIRouter(tags=["Schedule"])

@router.get("/{plan_id}", response_model=List[StudySessionResponse])
def get_full_schedule(
    plan_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    # Ensure plan belongs to user
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
        .order_by(StudySession.date)
        .all()
    )

    return sessions



@router.get("/{plan_id}/day/{target_date}", response_model=List[StudySessionResponse])
def get_schedule_by_day(
    plan_id: int,
    target_date: date,
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

    start = datetime.combine(target_date, datetime.min.time())
    end = datetime.combine(target_date, datetime.max.time())

    sessions = (
        db.query(StudySession)
        .filter(
            StudySession.plan_id == plan_id,
            StudySession.date >= start,
            StudySession.date <= end
        )
        .order_by(StudySession.date)
        .all()
    )

    return sessions


@router.put("/{plan_id}/session/{session_id}", response_model=StudySessionResponse)
def update_session(
    plan_id: int,
    session_id: int,
    data: StudySessionUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    # Verify plan belongs to user
    plan = (
        db.query(Plan)
        .filter(Plan.id == plan_id, Plan.user_id == current_user.id)
        .first()
    )

    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    session = (
        db.query(StudySession)
        .filter(
            StudySession.id == session_id,
            StudySession.plan_id == plan_id
        )
        .first()
    )

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    try:
        old_status = session.status
        # Update fields safely
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(session, field, value)

        new_status = session.status
        if old_status != new_status:
            if new_status == "completed":
                if not session.progress:
                    progress = Progress(
                        session_id=session.id,
                        completion_time=datetime.utcnow()
                    )
                    db.add(progress)
            elif old_status == "completed":
                if session.progress:
                    db.delete(session.progress)

        db.commit()
        db.refresh(session)
        return session
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update session")


@router.put("/session/{session_id}", response_model=StudySessionResponse)
def update_session_short(
    session_id: int,
    data: StudySessionUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Fallback route to support requests sent to /schedule/schedule/session/{session_id}.

    Finds the session by `session_id`, verifies the session's plan belongs to
    the `current_user`, and applies the same update logic as the main route.
    """
    # Find session
    session = db.query(StudySession).filter(StudySession.id == session_id).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Verify plan belongs to user
    plan = (
        db.query(Plan)
        .filter(Plan.id == session.plan_id, Plan.user_id == current_user.id)
        .first()
    )

    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    try:
        old_status = session.status
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(session, field, value)

        new_status = session.status
        if old_status != new_status:
            if new_status == "completed":
                if not session.progress:
                    progress = Progress(
                        session_id=session.id,
                        completion_time=datetime.utcnow()
                    )
                    db.add(progress)
            elif old_status == "completed":
                if session.progress:
                    db.delete(session.progress)

        db.commit()
        db.refresh(session)
        return session
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update session")







