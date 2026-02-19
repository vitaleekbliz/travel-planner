from typing import List, Dict
from datetime import datetime
from app.services.travel_manager.project.project import TravelProject
from app.services.travel_manager.errors.errors import *
from app.core.logger.logger import AppLogger
from app.api.models.models import *

class TravelManager:
    _instance = None
    _logger = AppLogger("TRAVELMANAGER", "travel_manager.log")

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TravelManager, cls).__new__(cls)
            cls._instance._initialized = True
        return cls._instance

    def __init__(self):
        # If we've already set up the data, don't do it again!
        if self._initialized:
            return
        
        self._projects: Dict[int, TravelProject] = {}
        self._initialized = True
        self._logger.logger.info("TravelManager initialized!")


    def create_project(self, name: str, description: str | None = None, start_date: datetime | None = None) -> TravelProject:
        """Creates a new project and stores it."""
        project = TravelProject(name, description, start_date)
        self._projects[project._id] = project
        self._logger.logger.info(f"Project {project._id} added to manager.")
        return project

    def get_project(self, project_id: int) -> TravelProject:
        """Finds a project by ID or raises an error."""
        project = self._projects.get(project_id)
        if not project:
            self._logger.logger.error(f"Project {project_id} not found.")
            raise ProjectNotFoundError(project_id)
        return project

    def list_projects(self) -> List[TravelProject]:
        #TODO conver to response type
        """Returns all managed projects."""
        return list(self._projects.values())

    def remove_project(self, project_id: int):
        """Removes a project if it's deletable (no visited places)."""
        project = self.get_project(project_id)
        
        if not project.is_deletable():
            self._logger.logger.warning(f"Attempted to delete project {project_id} with visited places.")
            raise ProjectIsNotDeletableError(project_id)
            
        del self._projects[project_id]
        self._logger.logger.info(f"Project {project_id} removed successfully.")

    def update_project(self, project_id: int, **kwargs):
        #TODO change to response model
        """Updates project details dynamically."""
        project = self.get_project(project_id)
        project.update_project(
            name=kwargs.get("name", project._name),
            description=kwargs.get("description", project._description),
            start_date=kwargs.get("start_date", project._start_date)
        )