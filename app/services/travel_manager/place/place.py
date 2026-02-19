from app.core.logger.logger import AppLogger
from app.api.models.models import *

class ProjectPlace:
    _place_logger = AppLogger("PROJECTPLACE", "project_place.log")
    _id_counter = 0

    def __init__(self, name: str, artic_id: int, note: str | None = None):
        self._id = self._id_counter
        ProjectPlace._id_counter+=1
        
        self._artic_id = artic_id
        self._note = note
        self._name = name
        self._visited = False
        self._place_logger.logger.info(f"Created place {self._id}")

    def get_response_model(self)->PlaceResponse:
        model = PlaceResponse(
            name=self._name,
            note=self._note,
            id=self._id,
            visited=self._visited
        )
        return model

    def update_place(self, name: str, note: str | None = None):
        self._note = note
        self._name = name
        self._place_logger.logger.info(f"Updated place {self._id}")

    def mark_visited(self):
        """Unmarking is prohibited same as deleting projects that contain marked Places"""
        self._visited = True
        self._place_logger.logger.info(f"Masked place {self._id} as visited")

    def is_visited(self):
        return self._visited