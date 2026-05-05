from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import models, schemas, auth

router = APIRouter(prefix="/moods", tags=["Moods"])


@router.post("/", response_model=schemas.MoodOut, status_code=201)
def create_mood(
    mood_data: schemas.MoodCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    mood = models.Mood(**mood_data.model_dump(), user_id=current_user.id)
    db.add(mood)
    db.commit()
    db.refresh(mood)
    return mood


@router.get("/", response_model=List[schemas.MoodOut])
def list_moods(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    return db.query(models.Mood).filter(models.Mood.user_id == current_user.id).all()


@router.get("/{mood_id}", response_model=schemas.MoodOut)
def get_mood(
    mood_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    mood = db.query(models.Mood).filter(
        models.Mood.id == mood_id, models.Mood.user_id == current_user.id
    ).first()
    if not mood:
        raise HTTPException(status_code=404, detail="Mood not found")
    return mood


@router.put("/{mood_id}", response_model=schemas.MoodOut)
def update_mood(
    mood_id: int,
    mood_data: schemas.MoodUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    mood = db.query(models.Mood).filter(
        models.Mood.id == mood_id, models.Mood.user_id == current_user.id
    ).first()
    if not mood:
        raise HTTPException(status_code=404, detail="Mood not found")

    for key, value in mood_data.model_dump(exclude_unset=True).items():
        setattr(mood, key, value)

    db.commit()
    db.refresh(mood)
    return mood


@router.delete("/{mood_id}", status_code=204)
def delete_mood(
    mood_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    mood = db.query(models.Mood).filter(
        models.Mood.id == mood_id, models.Mood.user_id == current_user.id
    ).first()
    if not mood:
        raise HTTPException(status_code=404, detail="Mood not found")
    db.delete(mood)
    db.commit()
