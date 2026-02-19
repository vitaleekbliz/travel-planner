from datetime import datetime
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List

class ProjectShema(BaseModel):
    name: str
    description:str | None = None
    start_date: datetime | None = None

class PlaceSchema(BaseModel):
    name:str
    note:str | None = None

# --- Place Schemas ---
class PlaceCreate(PlaceSchema):
    pass  

class PlaceUpdate(PlaceSchema):
    pass

class PlaceResponse(PlaceSchema):
    id: str
    visited: bool

# --- Project Schemas ---
class ProjectCreate(ProjectShema):
    # Allows creating project + places in one go
    places: List[PlaceSchema] = Field(default_factory=list, max_items=10)

class ProjectUpdate(ProjectShema):
    pass

class ProjectResponse(ProjectShema):
    id: int
    places: List[PlaceResponse]