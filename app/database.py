from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

# 1. Get the connection string from your central config
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# 2. Create the Engine
# The engine is the actual connection to the PostgreSQL database
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 3. Create a SessionLocal class
# Each instance of SessionLocal will be a database session.
# We set autocommit/autoflush to False to have full control over transactions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Create the Base class
# Our SQLAlchemy models will inherit from this class
Base = declarative_base()

# 5. Dependency: Get DB session
# This is a helper function used in FastAPI routes to get a database connection.
# Using 'yield' ensures the session is closed after the API request is done.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
