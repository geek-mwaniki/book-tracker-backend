from pydantic import BaseModel
from typing import Optional

class BookBase(BaseModel):
    title: str
    author: str
    pages: int = 0
    current_page: int = 0  # <--- Added this
    status: str = "To Read"

class BookCreate(BookBase):
    pass

class BookResponse(BookBase):
    id: int
    progress_percent: float = 0.0 # <--- Calculated field
    file_path: Optional[str] = None # <--- Path to your file

    class Config:
        from_attributes = True