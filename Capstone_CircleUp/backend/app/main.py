"""
CircleUp API entrypoint.

Routers are registered here as they're built (auth, users, activities,
participation). Keeping this file thin — it should only ever wire things
together, never contain business logic.
"""

import logging
import logging.config
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app.core.config import settings
from app.routers import auth, users, activities, participation

# ── Logging Configuration ─────────────────────────────────────────────────────

LOGS_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "detailed": {
            "format": (
                "%(asctime)s | %(levelname)-8s | %(name)s | "
                "%(funcName)s:%(lineno)d | %(message)s"
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": "INFO",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "detailed",
            "level": "DEBUG",
            "filename": os.path.join(LOGS_DIR, "circleup.log"),
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 3,
            "encoding": "utf-8",
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "detailed",
            "level": "ERROR",
            "filename": os.path.join(LOGS_DIR, "circleup_errors.log"),
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 3,
            "encoding": "utf-8",
        },
    },
    "loggers": {
        "app": {
            "level": "DEBUG",
            "handlers": ["console", "file", "error_file"],
            "propagate": False,
        },
        "uvicorn": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
        "sqlalchemy.engine": {
            "level": "WARNING",
            "handlers": ["file"],
            "propagate": False,
        },
    },
    "root": {
        "level": "WARNING",
        "handlers": ["console"],
    },
}

logging.config.dictConfig(LOGGING_CONFIG)

# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="CircleUp API",
    description="""
## CircleUp — Discover and Organise Social Activities

CircleUp is a platform that helps users discover and organise social activities
such as cricket matches, café meetups, study groups, and weekend trips.

### Key Features
- **Authentication** — Register, login, and manage your profile with JWT-based auth
- **Activity Management** — Create, edit, cancel, and browse activities
- **Participation** — Request to join activities; creators approve or reject requests
- **Contact Visibility** — Contact info is revealed only after a request is approved
- **Dashboard** — Track activities you created, joined, and requested

### Authentication
All endpoints except `/auth/register` and `/auth/login` require a Bearer token.

Use the **Authorize** button (🔒) at the top right to enter your token:
```
Bearer <your_access_token>
```
    """,
    version="1.0.0",
    contact={
        "name": "Tulika Lunkad",
        "email": "tulika2504@gmail.com",
    },
    license_info={
        "name": "Capstone Project",
    },
    openapi_tags=[
        {
            "name": "Auth",
            "description": "Register, login, and logout. JWT token is returned on login.",
        },
        {
            "name": "Users",
            "description": "View and update your own profile.",
        },
        {
            "name": "Activities",
            "description": (
                "Create, browse, edit, and cancel activities. "
                "Only the creator can edit or cancel their own activity."
            ),
        },
        {
            "name": "Participation",
            "description": (
                "Request to join activities. Creators can approve or reject requests. "
                "Contact info is revealed only after approval."
            ),
        },
        {
            "name": "Health",
            "description": "Service health check.",
        },
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
    "/",
    tags=["Health"],
    summary="Health check",
    description="Returns service status. Use this to confirm the API is running.",
)
def health_check():
    return {"status": "ok", "service": settings.PROJECT_NAME}


# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(auth.router,          prefix=settings.API_V1_PREFIX)
app.include_router(users.router,         prefix=settings.API_V1_PREFIX)
app.include_router(activities.router,    prefix=settings.API_V1_PREFIX)
app.include_router(participation.router, prefix=settings.API_V1_PREFIX)