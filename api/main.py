#api/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from api.routers import chat
# from api.routers import match
# from api.routers import admin
from app.logging import setup_logging
import os
from dotenv import load_dotenv


print("🚀 FastAPI app starting...")


load_dotenv()
setup_logging()

app = FastAPI(title="AI Resume Backend")

@app.on_event("startup")
def load_routers():
    print("🔥 Importing routers...")

    from api.routers import chat, match, admin

    app.include_router(chat.router)
    app.include_router(match.router)
    app.include_router(admin.router)

    print("✅ Routers loaded")

FRONTEND_URL = os.getenv("NEXT_PUBLIC_FRONTEND_URL","*")


# 🔥 REQUIRED for React
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.include_router(chat.router)
# app.include_router(match.router)
# app.include_router(admin.router)



@app.get("/health")
def health():
    return {"status": "ok"}

