from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from . import models
from .database import engine, SessionLocal

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="My Book Tracker API")

# This helper function handles opening/closing the database connection
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to your Book Tracker!"}

# --- NEW STUFF BELOW ---

@app.post("/books/")
def create_book(title: str, author: str, pages: int, db: Session = Depends(get_db)):
    # 1. Create a new Book object using our Model
    new_book = models.Book(title=title, author=author, pages=pages)
    
    # 2. Add it to the database "session"
    db.add(new_book)
    
    # 3. Commit (Save) the changes
    db.commit()
    
    # 4. Refresh to get the ID created by the database
    db.refresh(new_book)
    
    return {"message": "Book added successfully!", "book": new_book}

# ... (existing imports and get_db function)

@app.get("/books/")
def get_all_books(db: Session = Depends(get_db)):
    # This tells SQLAlchemy: "Select * From Books"
    books = db.query(models.Book).all()
    return books

# Add a route to find a specific book by its ID
@app.get("/books/{book_id}")
def get_single_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        return {"error": "Book not found!"}
    return book