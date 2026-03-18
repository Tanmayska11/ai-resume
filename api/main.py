from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

print("🔥 Starting FastAPI app...")

app = FastAPI(title="AI Resume Backend")

# --- Health routes ---
@app.get("/")
def root():
    return {"message": "server running"}

@app.get("/health")
def health():
    return {"status": "ok"}

# --- CORS ---
try:
    FRONTEND_URL = os.getenv("NEXT_PUBLIC_FRONTEND_URL", "*")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[FRONTEND_URL],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    print("✅ CORS loaded")

except Exception as e:
    print("❌ CORS failed:", str(e))


# --- Logging ---
try:
    from app.logging import setup_logging
    setup_logging()
    print("✅ Logging loaded")

except Exception as e:
    print("❌ Logging failed:", str(e))


# --- Routers ---
try:
    from api.routers import chat
    app.include_router(chat.router)
    print("✅ Chat router loaded")

except Exception as e:
    print("❌ Chat router failed:", str(e))


try:
    from api.routers import match
    app.include_router(match.router)
    print("✅ Match router loaded")

except Exception as e:
    print("❌ Match router failed:", str(e))


try:
    from api.routers import admin
    app.include_router(admin.router)
    print("✅ Admin router loaded")

except Exception as e:
    print("❌ Admin router failed:", str(e))