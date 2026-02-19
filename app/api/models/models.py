from datetime import datetime
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List

# --- Place Schemas ---
class PlaceSchema(BaseModel):
    name:str
    note:str | None = None

class PlaceCreate(PlaceSchema):
    pass  

class PlaceUpdate(PlaceSchema):
    id: int
    pass

class PlaceResponse(PlaceSchema):
    id: int
    visited: bool

# --- Project Schemas ---
class ProjectShema(BaseModel):
    name: str
    description:str | None = None
    start_date: datetime | None = None

class ProjectCreate(ProjectShema):
    # Allows creating project + places in one go
    places: list[PlaceCreate] | None = Field(default=None, max_items=10)

class ProjectUpdate(ProjectShema):
    id: int
    pass

class ProjectResponse(ProjectShema):
    id: int
    places: List[PlaceResponse] | None = None