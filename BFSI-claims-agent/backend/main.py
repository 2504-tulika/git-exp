from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.agents import claims_agent
from src.config.settings import settings
from src.exceptions.exceptions import register_exception_handlers
from src.routers import auth_router, claims_router, health_router
from src.utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application starting up -- warming up the agent")
    await claims_agent.warm_up()
    logger.info("Startup complete -- ready to accept requests")

    yield

    logger.info("Application shutting down")
    await claims_agent.shutdown()


app = FastAPI(title="Claims Processing Agent", lifespan=lifespan)

register_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_allowed_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(claims_router.router)
app.include_router(health_router.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


