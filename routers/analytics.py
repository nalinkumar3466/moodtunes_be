from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from database import get_db
import models, schemas, auth

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/", response_model=schemas.AnalyticsOut)
def get_analytics(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    # Total logs
    total_logs = (
        db.query(func.count(models.MoodLog.id))
        .filter(models.MoodLog.user_id == current_user.id)
        .scalar()
    )

    # Logs this week
    logs_this_week = (
        db.query(func.count(models.MoodLog.id))
        .filter(
            models.MoodLog.user_id == current_user.id,
            models.MoodLog.logged_at >= week_ago,
        )
        .scalar()
    )

    # Logs this month
    logs_this_month = (
        db.query(func.count(models.MoodLog.id))
        .filter(
            models.MoodLog.user_id == current_user.id,
            models.MoodLog.logged_at >= month_ago,
        )
        .scalar()
    )

    # Mood frequency
    mood_freq_rows = (
        db.query(
            models.Mood.name,
            models.Mood.color,
            func.count(models.MoodLog.id).label("count"),
        )
        .join(models.MoodLog, models.MoodLog.mood_id == models.Mood.id)
        .filter(models.MoodLog.user_id == current_user.id)
        .group_by(models.Mood.name, models.Mood.color)
        .order_by(func.count(models.MoodLog.id).desc())
        .all()
    )

    mood_frequencies = [
        schemas.MoodFrequency(mood_name=r.name, mood_color=r.color, count=r.count)
        for r in mood_freq_rows
    ]

    most_logged_mood = mood_frequencies[0].mood_name if mood_frequencies else None

    return schemas.AnalyticsOut(
        total_logs=total_logs or 0,
        mood_frequencies=mood_frequencies,
        most_logged_mood=most_logged_mood,
        logs_this_week=logs_this_week or 0,
        logs_this_month=logs_this_month or 0,
    )
