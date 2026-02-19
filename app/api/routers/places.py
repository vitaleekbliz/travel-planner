from fastapi import APIRouter, HTTPException, status, Query, Depends
from app.api.models.models import *
from app.services.travel_manager.errors.errors import *
from app.services.travel_manager.travel_manager import TravelManager

router = APIRouter(prefix="/projects/{project_id}/places", tags=["Places"])

async def get_travel_manager()->TravelManager:
    return TravelManager()

@router.post("/", response_model=PlaceResponse, status_code=status.HTTP_201_CREATED)
async def add_place_to_project(project_id: int, place_data: PlaceCreate, travel_manager:TravelManager = Depends(get_travel_manager)):
    """
    Validates the place via Artic API and adds it to the project if 
    the project isn't full and the place isn't a duplicate.
    """
    try:
        # The manager handles the 3 checks: Limit, Duplicate, and Artic Validation
        new_place = await travel_manager.add_place_to_project(project_id, place_data)
        return new_place
        
    except ProjectNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    except PlaceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except (DuplicatePlaceError, ProjectHasMaxPlacesAllowedError) as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.patch("/{place_id}/visited", response_model=PlaceResponse)
async def mark_visited(project_id: int, place_id: int, travel_manager:TravelManager = Depends(get_travel_manager)):
    """
    Sets visited = True. Returns 400 if user tries to unmark or if place doesn't exist.
    """
    try:
        updated_project = travel_manager.mark_place_visited(project_id, place_id)
        return updated_project
    except (ProjectNotFoundError, PlaceNotFoundError) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))