from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
import models
from routers import auth, moods, songs, mood_logs, recommendations, analytics

# Create all tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Mood-Based Smart Recommendation System",
    description="A multi-user API for mood management and song recommendations",
    version="1.0.0",
)

# CORS — allow React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://moodtunes-fe.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(moods.router)
app.include_router(songs.router)
app.include_router(mood_logs.router)
app.include_router(recommendations.router)
app.include_router(analytics.router)


@app.get("/", tags=["Root"])
def root():
    return {"message": "Mood Recommendation API is running 🎵"}
