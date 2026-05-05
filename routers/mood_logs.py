from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from database import get_db
import models, schemas, auth

router = APIRouter(prefix="/mood-logs", tags=["Mood Logs"])


@router.post("/", response_model=schemas.MoodLogOut, status_code=201)
def log_mood(
    log_data: schemas.MoodLogCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    # Verify mood belongs to user
    mood = db.query(models.Mood).filter(
        models.Mood.id == log_data.mood_id, models.Mood.user_id == current_user.id
    ).first()
    if not mood:
        raise HTTPException(status_code=404, detail="Mood not found")

    log = models.MoodLog(**log_data.model_dump(), user_id=current_user.id)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.get("/", response_model=List[schemas.MoodLogOut])
def get_mood_history(
    mood_id: Optional[int] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    query = db.query(models.MoodLog).filter(models.MoodLog.user_id == current_user.id)

    if mood_id:
        query = query.filter(models.MoodLog.mood_id == mood_id)

    return (
        query.order_by(models.MoodLog.logged_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.delete("/{log_id}", status_code=204)
def delete_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    log = db.query(models.MoodLog).filter(
        models.MoodLog.id == log_id, models.MoodLog.user_id == current_user.id
    ).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    db.delete(log)
    db.commit()
