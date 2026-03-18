from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas  # Added schemas here
from .database import engine, SessionLocal

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="My Book Tracker API")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 1. THE ROOT ROUTE
@app.get("/")
def read_root():
    return {"message": "Welcome to your Book Tracker!"}

#2. CREATE A BOOK
# Updated POST route using the Schema
@app.post("/books/", response_model=schemas.BookResponse)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    new_book = models.Book(**book.dict()) # This "unpacks" the dictionary into the model
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book

#3. GET ALL BOOKS

@app.get("/books/", response_model=list[schemas.BookResponse])
def get_all_books(db: Session = Depends(get_db)):
    return db.query(models.Book).all()

#4. GET A SINGLE BOOK BY ID

@app.get("/books/{book_id}", response_model=schemas.BookResponse)
def get_single_book(book_id: int, db: Session = Depends(get_db)):
    # 1. Look for the book in the database
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    
    # 2. If it's not there, raise a proper "404" error
    if not book:
        raise HTTPException(status_code=404, detail="Book not found in your library")
        
    # 3. If it IS there, return the book object
    return book

# 5. SEARCH BY AUTHOR
@app.get("/search/", response_model=list[schemas.BookResponse])
def search_books(author: str, db: Session = Depends(get_db)):
    return db.query(models.Book).filter(models.Book.author == author).all()

# 6. UPDATE BOOK STATUS
@app.patch("/books/{book_id}/status", response_model=schemas.BookResponse)
def update_book_status(book_id: int, new_status: str, db: Session = Depends(get_db)):
    # 1. Find the book
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    
    # 2. If it doesn't exist, throw an error
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    # 3. Update the status
    book.status = new_status
    
    # 4. Save to the database
    db.commit()
    db.refresh(book)
    
    return book
