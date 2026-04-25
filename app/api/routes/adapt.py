from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated
from datetime import datetime, timedelta
from collections import defaultdict

from app.db.session import get_db
from app.models.plan import Plan
from app.models.study_session import StudySession
from app.models.subject import Subject
from app.models.user import User

from app.api.routes.auth import get_current_user


router = APIRouter(tags=["Adaptive Planning"])


@router.post("/{plan_id}/recalculate")
def recalculate_plan(
    plan_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    # ------------------------
    # Validate plan
    # ------------------------
    plan = (
        db.query(Plan)
        .filter(Plan.id == plan_id, Plan.user_id == current_user.id)
        .first()
    )

    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    now = datetime.utcnow()

    # ------------------------
    # Fetch sessions
    # ------------------------
    sessions = (
        db.query(StudySession)
        .filter(StudySession.plan_id == plan_id)
        .all()
    )

    if not sessions:
        raise HTTPException(status_code=400, detail="No sessions found")

    # ------------------------
    # Separate sessions
    # ------------------------
    completed = [s for s in sessions if s.status == "completed"]
    pending_future = [s for s in sessions if s.status == "pending" and s.date >= now]
    missed = [s for s in sessions if s.status == "missed"]

    # ------------------------
    # Remaining workload per subject
    # ------------------------
    remaining_by_subject = defaultdict(int)

    for s in sessions:
        if s.status != "completed":
            remaining_by_subject[s.subject_id] += s.duration

    # ------------------------
    # Get subjects
    # ------------------------
    subjects = (
        db.query(Subject)
        .filter(Subject.user_id == current_user.id)
        .all()
    )

    subject_map = {s.id: s for s in subjects}

    # ------------------------
    # Remove only future pending sessions
    # ------------------------
    for s in pending_future:
        db.delete(s)

    db.commit()

    # ------------------------
    # Rebuild schedule intelligently
    # ------------------------
    new_sessions = []

    for subject_id, remaining_minutes in remaining_by_subject.items():
        subject = subject_map.get(subject_id)
        if not subject:
            continue

        # Days left until exam
        days_left = (subject.exam_date - now).days

        if days_left <= 0:
            continue

        # PRIORITY FACTOR
        # - difficulty ↑
        # - urgency ↑ (less days left)
        priority = subject.difficulty * (1 / days_left)

        daily_minutes = max(int((remaining_minutes / days_left) * (1 + priority)), 10)

        for i in range(days_left):
            day = now + timedelta(days=i)

            session = StudySession(
                plan_id=plan.id,
                subject_id=subject.id,
                date=day,
                duration=daily_minutes,
                status="pending"
            )

            new_sessions.append(session)

    db.add_all(new_sessions)
    db.commit()

    return {
        "message": "Plan recalculated",
        "subjects_updated": len(remaining_by_subject),
        "new_sessions": len(new_sessions)
    }



