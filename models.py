from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Float, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    moods = relationship("Mood", back_populates="owner", cascade="all, delete")
    mood_logs = relationship("MoodLog", back_populates="user", cascade="all, delete")


class Mood(Base):
    __tablename__ = "moods"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    color = Column(String(20), nullable=True)  # hex color for UI
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship("User", back_populates="moods")
    songs = relationship("Song", back_populates="mood", cascade="all, delete")
    mood_logs = relationship("MoodLog", back_populates="mood")


class Song(Base):
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    artist = Column(String(200), nullable=False)
    album = Column(String(200), nullable=True)
    genre = Column(String(100), nullable=True)
    energy_level = Column(Integer, nullable=True)  # 1-10
    tags = Column(String(500), nullable=True)  # comma-separated tags
    mood_id = Column(Integer, ForeignKey("moods.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    mood = relationship("Mood", back_populates="songs")


class MoodLog(Base):
    __tablename__ = "mood_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    mood_id = Column(Integer, ForeignKey("moods.id"), nullable=False)
    note = Column(Text, nullable=True)
    logged_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="mood_logs")
    mood = relationship("Mood", back_populates="mood_logs")
