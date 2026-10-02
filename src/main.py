from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.config import settings
from src.api import webhook, health
import logging

logging.basicConfig(level=settings.log_level.upper())
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Home Clinic WhatsApp Booking Agent")
    yield
    logger.info("Shutting down")


app = FastAPI(
    title="Home Clinic WhatsApp Booking Agent",
    description="WhatsApp booking platform for home healthcare",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(webhook.router)
app.include_router(health.router)
from src.api import admin
app.include_router(admin.router)


@app.get("/")
async def root():
    return {"message": "Home Clinic WhatsApp Booking Agent"}
