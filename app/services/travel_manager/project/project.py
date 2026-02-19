from app.services.travel_manager.place.place import ProjectPlace
from datetime import datetime
from typing import List
from app.services.travel_manager.errors.errors import *
from app.core.config.config import travel_project_settings
from app.core.logger.logger import AppLogger
from app.api.models.models import *


class TravelProject():
    _id_counter = 0
    _travel_logger = AppLogger("TRAVELPROJECT", "travel_project.log")

    def __init__(self, name: str, description:str | None = None, start_date: datetime | None = None):
        self._id = self._id_counter
        TravelProject._id_counter+=1

        self._name = name
        self._description = description
        self._start_date = start_date
        self._project_places: List[ProjectPlace] = []

        self._travel_logger.logger.info(f"Created new project {self._id}")

    def get_response_model(self)->ProjectResponse:
        model = ProjectResponse(
            id=self._id,
            name=self._name,
            description=self._description,
            start_time=self._start_date,
            #TODO debug the result
            places=[pl.get_response_model() for pl in self._project_places]
        )
        return model

    def add_place(self, artic_id: int, place_create: PlaceCreate, place_limit:int = travel_project_settings.PLACES_LIMIT) -> PlaceResponse:
        if any(pp._artic_id == artic_id for pp in self._project_places):
            self._travel_logger.logger.error("Trying to add dublicate place to project")
            raise DuplicatePlaceError(id, self._id)
        
        if(len(self._project_places) >= place_limit):
            self._travel_logger.logger.error("Trying to add place to full project")
            raise ProjectHasMaxPlacesAllowedError(self._id)
        
        self._travel_logger.logger.info(f"Adding place with artic id : {artic_id}")

        new_place = ProjectPlace(place_create.name, artic_id, place_create.note)
        self._project_places.append(new_place)

        return new_place.get_response_model()

    def update_project(self, project_update: ProjectUpdate):
        self._name = project_update.name
        self._description = project_update.description
        self._start_date = project_update.start_date
        self._travel_logger.logger.info(f"Updated project {self._id}")

    def update_place(self, place_update: PlaceUpdate):
        project_place = next((x for x in self._project_places if x._id == place_update.id), None)

        if not project_place:
            self._travel_logger.logger.error("Place id is not found in project")
            raise PlaceNotFoundError(place_update.id, self._id)
        
        self._travel_logger.logger.info(f"Updated place {place_update.id}")
        project_place.update_place(place_update.name, place_update.note)

    def mark_place_visited(self, place_id:int) -> PlaceResponse:
        project_place = next((x for x in self._project_places if x._id == place_id), None)

        if not project_place:
            raise PlaceNotFoundError(place_id, self._id)
        

        self._travel_logger.logger.info(f"Marked place {place_id} as visited")
        project_place.mark_visited()

        return project_place.get_response_model()


    def is_deletable(self)->bool:
        """Can't delete project with any marked places"""
        for pp in self._project_places:
            if pp.is_visited():
                return False
            
        return True

#TODO remove debug
if __name__ == "__main__":
    print("--- Starting Debug Session ---")
    
    try:
        # 1. Initialize Project
        my_trip = TravelProject(
            name="Summer Trip 2026", 
            description="Europe backpacking", 
            start_date=datetime(2026, 6, 1)
        )
        print(f"Project Created: {my_trip._name} (ID: {my_trip._id})")

        # 2. Add Places
        my_trip.add_place("Paris", id=101, note="Visit the Louvre")
        my_trip.add_place("Berlin", id=102, note="Try Currywurst")
        print(f"Added places. Current count: {len(my_trip._project_places)}")

        # 3. Test Duplicate Error (Triggering Debug)
        print("\nTesting DuplicatePlaceError...")
        try:
            my_trip.add_place("Fake Paris", id=101) # Duplicate ID
        except DuplicatePlaceError as e:
            print(f"Caught expected error: {e}")

        # 4. Test Visited Logic & Deletability
        print(f"\nIs project deletable? {my_trip.is_deletable()}")
        
        print("Marking Berlin as visited...")
        my_trip.mark_place_visited(102)
        
        print(f"Is project deletable now? {my_trip.is_deletable()} (Expected: False)")

        # 5. Test Missing Place Error
        print("\nTesting PlaceNotFoundError...")
        try:
            my_trip.update_place(place_id=999, name="Nowhere")
        except PlaceNotFoundError as e:
            print(f"Caught expected error: {e}")

    except Exception as e:
        print(f"An unexpected system error occurred: {e}")
        # This is where you'd look at travel_project.log for the AppLogger output