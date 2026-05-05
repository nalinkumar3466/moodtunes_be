from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from database import get_db
import models, schemas, auth

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("/", response_model=List[schemas.SongOut])
def get_recommendations(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    """
    Dynamic recommendations based on:
    1. User's most frequently logged moods (last 30 days)
    2. Songs from those moods, weighted by mood frequency
    3. If no logs, return songs from all moods randomly
    """
    from datetime import datetime, timedelta
    from sqlalchemy import desc
    import random

    thirty_days_ago = datetime.utcnow() - timedelta(days=30)

    # Get mood frequency for last 30 days
    mood_frequency = (
        db.query(models.MoodLog.mood_id, func.count(models.MoodLog.id).label("freq"))
        .filter(
            models.MoodLog.user_id == current_user.id,
            models.MoodLog.logged_at >= thirty_days_ago,
        )
        .group_by(models.MoodLog.mood_id)
        .order_by(desc("freq"))
        .all()
    )

    if mood_frequency:
        # Build weighted mood list (top 3 moods, weighted)
        top_moods = [mf.mood_id for mf in mood_frequency[:3]]

        songs = (
            db.query(models.Song)
            .filter(
                models.Song.user_id == current_user.id,
                models.Song.mood_id.in_(top_moods),
            )
            .all()
        )

        # Weight songs by how frequent their mood is
        weighted_songs = []
        mood_weights = {mf.mood_id: mf.freq for mf in mood_frequency[:3]}
        for song in songs:
            weight = mood_weights.get(song.mood_id, 1)
            weighted_songs.extend([song] * weight)

        random.shuffle(weighted_songs)
        # Deduplicate while preserving order
        seen = set()
        result = []
        for s in weighted_songs:
            if s.id not in seen:
                seen.add(s.id)
                result.append(s)
            if len(result) >= limit:
                break
        return result

    else:
        # Fallback: return all user songs shuffled
        songs = (
            db.query(models.Song)
            .filter(models.Song.user_id == current_user.id)
            .all()
        )
        random.shuffle(songs)
        return songs[:limit]


@router.get("/by-mood/{mood_id}", response_model=List[schemas.SongOut])
def get_recommendations_by_mood(
    mood_id: int,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    """Get song recommendations for a specific mood."""
    songs = (
        db.query(models.Song)
        .filter(
            models.Song.user_id == current_user.id,
            models.Song.mood_id == mood_id,
        )
        .all()
    )

    import random
    random.shuffle(songs)
    return songs[:limit]
