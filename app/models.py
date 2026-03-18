from sqlalchemy import Column, Integer, String, Float
from .database import Base

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    pages = Column(Integer)
    status = Column(String, default="To Read")  # To Read, Reading, Completed
    rating = Column(Float, nullable=True)      # 1.0 to 5.0 stars