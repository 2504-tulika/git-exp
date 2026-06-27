"""
CircleUp API entrypoint.

Routers are registered here as they're built (auth, users, activities,
participation). Keeping this file thin — it should only ever wire things
together, never contain business logic.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import auth, users

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="CircleUp — discover and organize social activities.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["health"])
def health_check():
    return {"status": "ok", "service": settings.PROJECT_NAME}


# Routers
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(users.router, prefix=settings.API_V1_PREFIX)