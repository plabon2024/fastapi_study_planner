from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import Annotated
from datetime import timedelta

from ics import Calendar, Event

from app.db.session import get_db
from app.models.plan import Plan
from app.models.study_session import StudySession
from app.models.subject import Subject
from app.models.user import User

from app.api.routes.auth import get_current_user


router = APIRouter(tags=["Export"])

@router.get("/{plan_id}/calendar")
def export_calendar(
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

    # ------------------------
    # Fetch sessions
    # ------------------------
    sessions = (
        db.query(StudySession)
        .filter(StudySession.plan_id == plan_id)
        .all()
    )

    if not sessions:
        raise HTTPException(status_code=400, detail="No sessions to export")

    # ------------------------
    # Fetch subjects (for naming)
    # ------------------------
    subjects = db.query(Subject).all()
    subject_map = {s.id: s.name for s in subjects}

    # ------------------------
    # Create calendar
    # ------------------------
    cal = Calendar()

    for session in sessions:
        subject_name = subject_map.get(session.subject_id, "Study")

        event = Event()
        event.name = f"{subject_name} Study Session"

        start_time = session.date
        end_time = session.date + timedelta(minutes=session.duration)

        event.begin = start_time
        event.end = end_time

        event.description = f"Duration: {session.duration} minutes | Status: {session.status}"

        cal.events.add(event)

    # ------------------------
    # Return .ics file
    # ------------------------
    return Response(
        content=str(cal),
        media_type="text/calendar",
        headers={
            "Content-Disposition": f"attachment; filename=study_plan_{plan_id}.ics"
        }
    )










