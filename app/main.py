import os
import shutil
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File # <--- MUST HAVE 'File' and 'UploadFile'
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from . import models, schemas
from .database import engine, SessionLocal
from fastapi.staticfiles import StaticFiles

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="My Book Tracker API")
# This tells FastAPI: "If someone asks for /files, look in the uploaded_books folder"
app.mount("/files", StaticFiles(directory="uploaded_books"), name="files")

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

# 5. ADVANCED SEARCH (Replaces the old Search by Author)
@app.get("/search/", response_model=list[schemas.BookResponse])
def search_books(author: str = None, min_pages: int = 0, db: Session = Depends(get_db)):
    # 1. Start with a basic query of all books
    query = db.query(models.Book)
    
    # 2. If the user provided an author, add a filter
    if author:
        query = query.filter(models.Book.author == author)
        
    # 3. Always filter by minimum pages (default is 0)
    query = query.filter(models.Book.pages >= min_pages)
    
    # 4. Run the final query and return results
    return query.all()
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
# 7. DELETE A BOOK
@app.delete("/books/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    # 1. Find the book first to make sure it exists
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    
    # 2. If it's not there, tell the user
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    # 3. If it is there, delete it from the session
    db.delete(book)
    
    # 4. Commit the change to the actual database file
    db.commit()
    
    return {"message": f"Book with ID {book_id} has been deleted successfully."}

# 8. ADD BOOK BY ISBN (Automated)
@app.post("/books/isbn/{isbn}", response_model=schemas.BookResponse)
async def add_book_by_isbn(isbn: str, db: Session = Depends(get_db)):
    # 1. Ask Open Library for the book info
    url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        data = response.json()

    # 2. Check if the book was actually found
    isbn_key = f"ISBN:{isbn}"
    if isbn_key not in data:
        raise HTTPException(status_code=404, detail="Book not found in Open Library")

    book_info = data[isbn_key]
    
    # 3. Create the new book record using fetched data
    new_book = models.Book(
        title=book_info.get("title", "Unknown Title"),
        author=book_info.get("authors", [{"name": "Unknown"}])[0]["name"],
        pages=book_info.get("number_of_pages", 0),
        status="To Read"
    )

    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    
    return new_book

# 9. UPLOAD A BOOK FILE
@app.post("/books/{book_id}/upload")
async def upload_book_file(book_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    # 1. First, check if the book even exists in our database
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    
    if not book:
        # This stops the code here and sends an error to your phone
        raise HTTPException(status_code=404, detail=f"Book with ID {book_id} not found. Create the book entry first!")

    # 2. Create a folder for files if it doesn't exist
    if not os.path.exists("uploaded_books"):
        os.makedirs("uploaded_books")

    # 3. Define where to save the file
    file_location = f"uploaded_books/{file.filename}"
    
    # 4. Save the actual file to your computer
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 5. Now it's safe to update the file_path because we know 'book' is not None
    book.file_path = file_location
    db.commit()

    return {"info": f"File '{file.filename}' saved for book ID {book_id}"}

# 10. DOWNLOAD / VIEW BOOK FILE
@app.get("/books/{book_id}/read")
def read_book_file(book_id: int, db: Session = Depends(get_db)):
    # 1. Find the book
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    
    # 2. Check if the book exists and has a file
    if not book or not book.file_path:
        raise HTTPException(status_code=404, detail="Book file not found. Have you uploaded it?")
    
    # 3. Check if the file actually exists on the computer disk
    if not os.path.exists(book.file_path):
        raise HTTPException(status_code=404, detail="File missing on server.")

    # 4. Send the file to your phone/browser
    return FileResponse(book.file_path)
