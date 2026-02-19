from fastapi import APIRouter, HTTPException, status, Query
from app.api.models.models import *

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(project_data: ProjectCreate):
    # Logic: 1. Create Project, 2. Validate & Add Places from Artic API
    pass

@router.get("/", response_model=List[ProjectResponse])
async def list_projects(
    limit: int = Query(10, le=100), 
    offset: int = 0,
    name_filter: str | None = None
):
    pass

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: int):
    pass

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: int):
    # Requirement: Validate if any place is visited before deleting
    # if project.has_visited_places(): raise HTTPException(400, "Cannot delete...")
    pass