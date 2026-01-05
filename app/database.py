# app/database.py
from app.config import settings
from sqlalchemy import create_engine

engine = create_engine(settings.DATABASE_URL)
# ... rest of your setup