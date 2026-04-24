from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated, List

from app.db.session import get_db
from app.models.subject import Subject
from app.models.user import User
from app.schemas.subject import (
    SubjectCreate,
    SubjectUpdate,
    SubjectResponse
)
from app.api.routes.auth import get_current_user


router = APIRouter(tags=["Subjects"])


# ------------------------
# CREATE SUBJECT
# ------------------------
@router.post("/", response_model=SubjectResponse)
def create_subject(
    data: SubjectCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    subject = Subject(
        user_id=current_user.id,
        name=data.name,
        difficulty=data.difficulty,
        estimated_hours=data.estimated_hours,
        exam_date=data.exam_date
    )

    db.add(subject)
    db.commit()
    db.refresh(subject)

    return subject


# ------------------------
# LIST SUBJECTS (USER ONLY)
# ------------------------
@router.get("/", response_model=List[SubjectResponse])
def get_subjects(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    subjects = (
        db.query(Subject)
        .filter(Subject.user_id == current_user.id)
        .all()
    )

    return subjects


# ------------------------
# GET ONE SUBJECT
# ------------------------
@router.get("/{subject_id}", response_model=SubjectResponse)
def get_subject(
    subject_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    subject = (
        db.query(Subject)
        .filter(
            Subject.id == subject_id,
            Subject.user_id == current_user.id
        )
        .first()
    )

    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    return subject


# ------------------------
# UPDATE SUBJECT
# ------------------------
@router.put("/{subject_id}", response_model=SubjectResponse)
def update_subject(
    subject_id: int,
    data: SubjectUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    subject = (
        db.query(Subject)
        .filter(
            Subject.id == subject_id,
            Subject.user_id == current_user.id
        )
        .first()
    )

    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    # Update only provided fields
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(subject, field, value)

    db.commit()
    db.refresh(subject)

    return subject


# ------------------------
# DELETE SUBJECT
# ------------------------
@router.delete("/{subject_id}")
def delete_subject(
    subject_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    subject = (
        db.query(Subject)
        .filter(
            Subject.id == subject_id,
            Subject.user_id == current_user.id
        )
        .first()
    )

    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    db.delete(subject)
    db.commit()

    return {"message": "Subject deleted successfully"}