from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
import models, schemas, auth

router = APIRouter(prefix="/songs", tags=["Songs"])


@router.post("/", response_model=schemas.SongOut, status_code=201)
def create_song(
    song_data: schemas.SongCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    # Verify mood belongs to user
    mood = db.query(models.Mood).filter(
        models.Mood.id == song_data.mood_id, models.Mood.user_id == current_user.id
    ).first()
    if not mood:
        raise HTTPException(status_code=404, detail="Mood not found")

    song = models.Song(**song_data.model_dump(), user_id=current_user.id)
    db.add(song)
    db.commit()
    db.refresh(song)
    return song


@router.get("/", response_model=List[schemas.SongOut])
def list_songs(
    mood_id: Optional[int] = Query(None),
    energy_level: Optional[int] = Query(None),
    genre: Optional[str] = Query(None),
    tags: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    query = db.query(models.Song).filter(models.Song.user_id == current_user.id)

    if mood_id:
        query = query.filter(models.Song.mood_id == mood_id)
    if energy_level is not None:
        query = query.filter(models.Song.energy_level == energy_level)
    if genre:
        query = query.filter(models.Song.genre.ilike(f"%{genre}%"))
    if tags:
        query = query.filter(models.Song.tags.ilike(f"%{tags}%"))

    return query.all()


@router.get("/{song_id}", response_model=schemas.SongOut)
def get_song(
    song_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    song = db.query(models.Song).filter(
        models.Song.id == song_id, models.Song.user_id == current_user.id
    ).first()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    return song


@router.put("/{song_id}", response_model=schemas.SongOut)
def update_song(
    song_id: int,
    song_data: schemas.SongUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    song = db.query(models.Song).filter(
        models.Song.id == song_id, models.Song.user_id == current_user.id
    ).first()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")

    update_data = song_data.model_dump(exclude_unset=True)

    # If mood_id is being changed, verify new mood belongs to user
    if "mood_id" in update_data:
        mood = db.query(models.Mood).filter(
            models.Mood.id == update_data["mood_id"], models.Mood.user_id == current_user.id
        ).first()
        if not mood:
            raise HTTPException(status_code=404, detail="Mood not found")

    for key, value in update_data.items():
        setattr(song, key, value)

    db.commit()
    db.refresh(song)
    return song


@router.delete("/{song_id}", status_code=204)
def delete_song(
    song_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    song = db.query(models.Song).filter(
        models.Song.id == song_id, models.Song.user_id == current_user.id
    ).first()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    db.delete(song)
    db.commit()
