from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.routers.project import router as project_router
from app.api.routers.places import router as place_router
from app.services.artic_place_fetcher.artic_place_fetcher import ArticPlaceFetcher
import asyncio
from datetime import datetime
from app.services.travel_manager.errors.errors import *
from app.services.artic_place_fetcher.errors.errors import *
from app.services.travel_manager.travel_manager import TravelManager
from app.api.models.models import *
import uvicorn

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup Logic ---
    # Initialize the Singleton Fetcher and load data into memory
    fetcher = ArticPlaceFetcher()
    print("Initializing Artic Place Fetcher cache...")
    await fetcher.fetch_all_places()
    print(f"Successfully cached {len(fetcher._places)} locations.")
    
    yield
    # --- Shutdown Logic ---
    print("Shutting down Travel Planner API...")

# Initialize FastAPI with the lifespan handler
app = FastAPI(
    title="Travel Planner API",
    version="1.0.0",
    lifespan=lifespan
)

# Include your routers
app.include_router(project_router)
app.include_router(place_router)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}