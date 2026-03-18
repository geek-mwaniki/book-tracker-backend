from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. This is the address of our local database file
SQLALCHEMY_DATABASE_URL = "sqlite:///./books.db"

# 2. The Engine is the actual connection pool
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 3. SessionLocal is what we use to actually talk to the DB in our routes
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. We will inherit from this class to create our models
Base = declarative_base()