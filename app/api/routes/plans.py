from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated, List
from datetime import datetime, timedelta

from app.db.session import get_db
from app.models.plan import Plan
from app.models.subject import Subject
from app.models.study_session import StudySession
from app.models.user import User

from app.schemas.plan import PlanResponse
from app.schemas.planner import PlanGenerateRequest

from app.api.routes.auth import get_current_user


router = APIRouter(tags=["Plans"])


@router.post("/generate", response_model=PlanResponse)
def generate_plan(
    data: PlanGenerateRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    subjects = (
        db.query(Subject)
        .filter(
            Subject.id.in_([s.subject_id for s in data.subjects]),
            Subject.user_id == current_user.id
        )
        .all()
    )

    if not subjects:
        raise HTTPException(status_code=400, detail="No valid subjects found")

    # ------------------------
    # Compute total hours
    # ------------------------
    total_hours = sum(s.estimated_hours for s in subjects)

    start_date = data.start_date
    end_date = max(s.exam_date for s in subjects)

    total_days = (end_date - start_date).days + 1
    if total_days <= 0:
        raise HTTPException(status_code=400, detail="Invalid date range")

    # ------------------------
    # Create plan
    # ------------------------
    plan = Plan(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
        total_hours=total_hours,
        status="active"
    )

    db.add(plan)
    db.commit()
    db.refresh(plan)

    # ------------------------
    # Simple weighted scheduling
    # ------------------------
    sessions = []

    for subject in subjects:
        days_left = (subject.exam_date - start_date).days + 1
        weight = subject.difficulty * (1 / max(days_left, 1))

        subject_hours = subject.estimated_hours

        # distribute across days
        daily_hours = subject_hours / max(days_left, 1)

        for i in range(days_left):
            session_date = start_date + timedelta(days=i)

            duration_minutes = int(daily_hours * 60)

            if duration_minutes <= 0:
                continue

            session = StudySession(
                plan_id=plan.id,
                subject_id=subject.id,
                date=session_date,
                duration=duration_minutes,
                status="pending"
            )

            sessions.append(session)

    db.add_all(sessions)
    db.commit()

    return plan


@router.get("/", response_model=List[PlanResponse])
def get_plans(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    return db.query(Plan).filter(Plan.user_id == current_user.id).all()

@router.get("/{plan_id}", response_model=PlanResponse)
def get_plan(
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

    return plan


@router.delete("/{plan_id}")
def delete_plan(
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

    db.delete(plan)
    db.commit()

    return {"message": "Plan deleted successfully"}



@router.post("/{plan_id}/regenerate")
def regenerate_plan(
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

    # Delete old sessions
    db.query(StudySession).filter(StudySession.plan_id == plan.id).delete()

    subjects = (
        db.query(Subject)
        .filter(Subject.user_id == current_user.id)
        .all()
    )

    # Re-run generation logic (reuse function ideally)
    sessions = []

    for subject in subjects:
        days_left = (subject.exam_date - plan.start_date).days + 1

        daily_hours = subject.estimated_hours / max(days_left, 1)

        for i in range(days_left):
            session_date = plan.start_date + timedelta(days=i)

            session = StudySession(
                plan_id=plan.id,
                subject_id=subject.id,
                date=session_date,
                duration=int(daily_hours * 60),
                status="pending"
            )
            sessions.append(session)

    db.add_all(sessions)
    db.commit()

    return {"message": "Plan regenerated"}


