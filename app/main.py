import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import CORS_ORIGINS
from app.api.routes import router
from app.services.agent_service import (
    session_service,
    close_agent_service,
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("stockline")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure the persistent session database is ready.
    await session_service.prepare_tables()
    logger.info("Stockline session database initialised.")

    yield

    await close_agent_service()
    logger.info("Stockline backend shut down.")


app = FastAPI(
    title="Stockline API",
    description="Multi-agent AI operating system for fast-fashion retail.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
async def root():
    return {
        "application": "Stockline",
        "status": "online",
        "message": "Welcome to the Stockline API.",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}