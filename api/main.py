#api/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import chat
from api.routers import match
from app.logging import setup_logging
from api.routers import admin
import os
from dotenv import load_dotenv



load_dotenv()
setup_logging()

app = FastAPI(title="AI Resume Backend")

FRONTEND_URL = os.getenv("NEXT_PUBLIC_FRONTEND_URL")


# 🔥 REQUIRED for React
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(match.router)
app.include_router(admin.router)



@app.get("/health")
def health():
    return {"status": "ok"}

