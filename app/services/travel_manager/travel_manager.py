from typing import List, Dict
from datetime import datetime
from app.services.travel_manager.project.project import TravelProject
from app.services.travel_manager.errors.errors import *
from app.services.artic_place_fetcher.errors.errors import *
from app.core.logger.logger import AppLogger
from app.api.models.models import *
from app.services.artic_place_fetcher.artic_place_fetcher import ArticPlaceFetcher


class TravelManager:
    _instance = None
    _logger = AppLogger("TRAVELMANAGER", "travel_manager.log")
    _artic_place_fetcher = ArticPlaceFetcher()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TravelManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        # If we've already set up the data, don't do it again!
        if self._initialized:
            return
        
        self._projects: Dict[int, TravelProject] = {}
        self._initialized = True
        self._logger.logger.info("TravelManager initialized!")

    def mark_place_visited(self, project_id: int, place_id: int) -> PlaceResponse:
        """
        Coordinates marking a place as visited. 
        Returns the updated ProjectPlace for the API response.
        """
        # 1. Get the project (raises ProjectNotFoundError if not found)
        project = self.get_project_by_id(project_id)
        if not project:
            raise ProjectNotFoundError(project_id)

        # 2. Delegate the logic to the project instance
        # This will raise PlaceNotFoundError if place_id isn't in this project
        updated_place_model = project.mark_place_visited(place_id)

        self._logger.logger.info(f"Place {place_id} in Project {project_id} marked as visited.")

        return updated_place_model

    async def add_place_to_project(self, project_id: int, place_data: PlaceCreate) -> PlaceResponse:
        # 1. Get the project instance (raises ProjectNotFoundError if missing)
        project = self.get_project_by_id(project_id)

        # 2. Validate against Artic API and get the official ID
        # This satisfies the requirement to validate before storing
        artic_id = self._artic_place_fetcher.get_place_id(place_data.name)
        if not artic_id:
            raise ArticPlaceNotFoundError(f"Can't find place in artic API name = {place_data.name}")

        # 3. Add to project
        # The project.add_place method handles Duplicate and Max Limit checks
        new_place_response = project.add_place(artic_id, place_data)

        self._logger.logger.info(f"Successfully added place {artic_id} to project {project_id}")
        return new_place_response

    #TODO replace return type with Pydantic Model
    def create_project(self, project_create:ProjectCreate) -> TravelProject:
        """Creates a new project and stores it."""
        #TODO replace constructors and other funtion parameters with Pydantic Models
        project = TravelProject(
            project_create.name,
            project_create.description,
            project_create.start_date
        )
        self._projects[project._id] = project
        self._logger.logger.info(f"Project {project._id} added to manager.")

        #create places for project
        if project_create.places:
            for place in project_create.places:
                found_artic_id = self._artic_place_fetcher.get_place_id(place.name)
                if found_artic_id:
                    self._logger.logger.info(f"Place is added to recently creted project")
                    project.add_place(found_artic_id, place)
                else:
                    self._logger.logger.warning(f"Place is not found in artic API : name = {place.name}")

        return project
    
    async def create_project(self, project_create: ProjectCreate) -> tuple[TravelProject, list[str]]:
        """Creates a new project and attempts to add all provided places."""
        warnings = []

        # 1. Initialize the project
        #TODO rewrite constructor to take in Model
        project = TravelProject(
            project_create.name,
            project_create.description,
            project_create.start_date
        )

        # 2. Add to internal registry immediately
        self._projects[project._id] = project
        self._logger.logger.info(f"Project {project._id} created.")

        # 3. Process places one by one
        if project_create.places:
            for place in project_create.places:
                try:
                    # Use our Singleton Fetcher to find the external ID
                    artic_id = self._artic_place_fetcher.get_place_id(place.name)

                    # add_place now handles duplicate and limit checks
                    project.add_place(artic_id, place)

                except (PlaceNotFoundError, DuplicatePlaceError, ProjectHasMaxPlacesAllowedError) as e:
                    # Instead of crashing, we record the problem
                    err_msg = str(e)
                    self._logger.logger.warning(f"Partial creation warning: {err_msg}")
                    warnings.append(err_msg)

        return project, warnings

    def get_project_by_id(self, project_id: int) -> TravelProject:
        """Finds a project by ID or raises an error."""
        project = self._projects.get(project_id)
        if not project:
            self._logger.logger.error(f"Project {project_id} not found.")
            raise ProjectNotFoundError(project_id)
        return project
    
    # def get_project_by_name(self, name: str) -> TravelProject:
    #     """Finds a project by name or raises an error."""
    #     project = next((p for p in self._projects.values() if p._name == name), None)
    #     if not project:
    #         self._logger.logger.error(f"Project \"{name}\" not found.")
    #         raise ProjectNotFoundError(name)
    #     return project

    def list_projects(self) -> List[ProjectResponse]:
        """Returns all managed projects."""
        return [x.get_response_model() for x in self._projects.values()]

    def remove_project(self, project_id: int):
        """Removes a project if it's deletable (no visited places)."""
        project = self.get_project_by_id(project_id)
        
        if not project.is_deletable():
            self._logger.logger.warning(f"Attempted to delete project {project_id} with visited places.")
            raise ProjectIsNotDeletableError(project_id)
            
        del self._projects[project_id]
        self._logger.logger.info(f"Project {project_id} removed successfully.")

    def update_project(self, project_update: ProjectUpdate):
        """Updates project details dynamically."""
        project = self.get_project_by_id(project_update.id)
        #TODO think about making name optional for update function
        if not project:
            self._logger.logger.error(f"Project {project_update.id} not found.")
            raise ProjectNotFoundError(project_update.id)
        
        project.update_project(project_update)