

class ProjectBaseError(Exception):
    """Base class for all exceptions in this project."""
    def __init__(self, message: str | None = None):
        self.message = message or "A project error occurred."
        super().__init__(self.message)

class PlaceNotFoundError(ProjectBaseError):
    """Raised when a specific project place ID is not found."""
    def __init__(self, place_id: int, project_id: int):
        self.place_id = place_id
        self.project_id = project_id
        super().__init__(f"Project (id = {project_id}) place with ID '{place_id}' could not be found.")

class DuplicatePlaceError(ProjectBaseError):
    """Raised when trying to add a place that already exists."""
    def __init__(self, place_id: int, project_id: int):
        self.place_id = place_id
        self.project_id = project_id
        super().__init__(f"Project (id = {project_id}) place with ID '{place_id}' already exists.")

class ProjectIsNotDeletableError(ProjectBaseError):
    """Raised when project has a MARKED place ."""
    def __init__(self, project_id: int):
        self.project_id = project_id
        super().__init__(f"Project with ID '{project_id}' has marked places.")

class ProjectHasMaxPlacesAllowedError(ProjectBaseError):
    """Raised when project has a MARKED place ."""
    def __init__(self, project_id: int):
        self.project_id = project_id
        super().__init__(f"Project with ID '{project_id}' has maximum places allowed places.")