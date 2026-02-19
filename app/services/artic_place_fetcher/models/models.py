from pydantic import BaseModel, HttpUrl
from typing import List, Optional

class ArticPlace(BaseModel):
    id: int
    title: str

class Pagination(BaseModel):
    total_pages: int
    next_url: Optional[HttpUrl] = None

class ArticResponse(BaseModel):
    pagination: Pagination
    data: List[ArticPlace]