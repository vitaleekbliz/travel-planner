from fastapi import APIRouter, HTTPException, status, Query
from app.api.models.models import *

router = APIRouter(prefix="/projects/{project_id}/places", tags=["Places"])

@router.post("/", response_model=PlaceResponse)
async def add_place_to_project(project_id: int, place_data: PlaceCreate):
    
    # 1. Check project limit (max 10)
    # 2. Check for duplicate external_id in this project
    # 3. Validate external_id exists in Artic API using ArticPlaceFetcher
    pass

@router.patch("/{place_id}/visited")
async def mark_visited(project_id: int, place_id: int):
    # Logic to set visited = True (Unmarking prohibited)
    pass