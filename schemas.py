from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# ── Auth ──────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class LoginRequest(BaseModel):
    username: str
    password: str


# ── Mood ──────────────────────────────────────────────────────────────────────

class MoodCreate(BaseModel):
    name: str
    description: Optional[str] = None
    color: Optional[str] = "#6366f1"

class MoodUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None

class MoodOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    color: Optional[str]
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# ── Song ──────────────────────────────────────────────────────────────────────

class SongCreate(BaseModel):
    title: str
    artist: str
    album: Optional[str] = None
    genre: Optional[str] = None
    energy_level: Optional[int] = None  # 1–10
    tags: Optional[str] = None
    mood_id: int

class SongUpdate(BaseModel):
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    genre: Optional[str] = None
    energy_level: Optional[int] = None
    tags: Optional[str] = None
    mood_id: Optional[int] = None

class SongOut(BaseModel):
    id: int
    title: str
    artist: str
    album: Optional[str]
    genre: Optional[str]
    energy_level: Optional[int]
    tags: Optional[str]
    mood_id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ── Mood Log ──────────────────────────────────────────────────────────────────

class MoodLogCreate(BaseModel):
    mood_id: int
    note: Optional[str] = None

class MoodLogOut(BaseModel):
    id: int
    user_id: int
    mood_id: int
    note: Optional[str]
    logged_at: datetime
    mood: MoodOut

    class Config:
        from_attributes = True


# ── Analytics ─────────────────────────────────────────────────────────────────

class MoodFrequency(BaseModel):
    mood_name: str
    mood_color: Optional[str]
    count: int

class AnalyticsOut(BaseModel):
    total_logs: int
    mood_frequencies: List[MoodFrequency]
    most_logged_mood: Optional[str]
    logs_this_week: int
    logs_this_month: int
