import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.agents import chat_agent, claims_agent
from src.config.settings import settings
from src.exceptions.exceptions import register_exception_handlers
from src.rag import retriever
from src.routers import auth_router, chat_router, claims_router, health_router
from src.utils.logger import get_logger

logger = get_logger(__name__)


async def _warm_up_policy_search():
    """
    Load the embedding model and policy index in THIS process. The claim
    review searches clauses inside the MCP subprocess (warmed by
    claims_agent.warm_up), but the chat assistants search here, so without
    this the first chat message after every restart pays the load time.
    If it fails, the app still starts and the search loads on first use.
    """
    try:
        await asyncio.to_thread(retriever.warm_up)
    except Exception as exc:
        logger.warning(f"Policy search warm-up failed -- it will load on first use instead: {exc}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application starting up -- warming up the agent and policy search")
    # The two loads are independent, so run them side by side.
    await asyncio.gather(claims_agent.warm_up(), _warm_up_policy_search())
    chat_agent.warm_up()
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
app.include_router(chat_router.router)
app.include_router(health_router.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
