from app.core.logger.logger import AppLogger


class ProjectPlace:
    _place_logger = AppLogger("PROJECTPLACE", "project_place.log")

    def __init__(self, name: str, id: int, note: str | None = None):
        self._id = id
        self._note = note
        self._name = name
        self._visited = False
        self._place_logger.logger.info(f"Created place {id}")


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