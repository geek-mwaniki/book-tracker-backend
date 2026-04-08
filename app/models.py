import os
import shutil
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from . import models, schemas
from .database import engine, SessionLocal
from sqlalchemy import Column, Integer, String, Float
from .database import Base  # <--- THIS IS THE MISSING LINE
# ... (rest of your existing code: get_db, routes, etc.)

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    pages = Column(Integer)
    current_page = Column(Integer, default=0)
    status = Column(String, default="To Read")  # To Read, Reading, Completed
    rating = Column(Float, nullable=True)      # 1.0 to 5.0 stars
    file_path = Column(String, nullable=True)  # This stores the location of the PDF/EPUB