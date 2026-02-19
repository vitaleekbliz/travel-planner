from fastapi import APIRouter, HTTPException, status, Query, Depends, Response
from app.api.models.models import *
from app.services.travel_manager.travel_manager import TravelManager
from app.services.travel_manager.errors.errors import *

router = APIRouter(prefix="/projects", tags=["Projects"])

async def get_travel_manager()->TravelManager:
    return TravelManager()

@router.post("/")
async def create_project(
    project_data: ProjectCreate, 
    response: Response,
    travel_manager: TravelManager = Depends(get_travel_manager)
):
    # Tuple unpacking: get project and the list of skipped places
    project, warnings = await travel_manager.create_project(project_data)
    
    if warnings:
        response.status_code = status.HTTP_207_MULTI_STATUS 
        result_status = "partial_success"
    else:
        response.status_code = status.HTTP_201_CREATED
        result_status = "success"

    return {
        "project": project.get_response_model(),
        "warnings": warnings,
        "status": result_status
    }

@router.get("/", response_model=List[ProjectResponse])
async def list_projects(
    limit: int = Query(10, le=100), 
    offset: int = 0,
    name_filter: str | None = None,
    travel_manager: TravelManager = Depends(get_travel_manager)
):
    """
    Lists projects with pagination and optional name filtering.
    """
    all_projects = travel_manager.list_projects()

    # Apply Filtering
    if name_filter:
        all_projects = [
            p for p in all_projects 
            if name_filter.lower() in p.name.lower()
        ]

    # Apply Slicing for Pagination
    return all_projects[offset : offset + limit]


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: int, travel_manager: TravelManager = Depends(get_travel_manager)):
    """
    Retrieves a single project by its ID.
    """
    try:
        return travel_manager.get_project_by_id(project_id).get_response_model()
    except ProjectNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=str(e)
        )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: int, travel_manager: TravelManager = Depends(get_travel_manager)):
    """
    Removes a project. Fails if any place in the project is marked 'visited'.
    """
    try:
        travel_manager.remove_project(project_id)
        # 204 No Content returns no body, just success.
        return 
    except ProjectNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=str(e)
        )
    except ProjectIsNotDeletableError as e:
        # 403 Forbidden is used because the server understands the request
        # but refuses to authorize it due to the business rule.
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail=str(e)
        )