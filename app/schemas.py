from pydantic import BaseModel
from typing import Optional

# This defines what data we expect when someone ADDS a book
class BookCreate(BaseModel):
    title: str
    author: str
    pages: Optional[int] = None
    status: str = "To Read"

# This defines what a book looks like when we SEND it back to the user
class BookResponse(BookCreate):
    id: int

    class Config:
        from_attributes = True