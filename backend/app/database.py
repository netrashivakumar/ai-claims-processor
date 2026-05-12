import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine,text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
# from .database import engine

# This finds the current file, goes up one folder, and looks for .env
env_path = Path(__file__).resolve().parent.parent / '.env'
# load_dotenv()
load_dotenv(dotenv_path=env_path)

# Add this temporary print to confirm the fix in your terminal
print(f"--- DEBUG: USERNAME IS {os.getenv('DATABASE_URL','NOT FOUND').split('://')[1].split(':')[0]} ---")

# This is a fallback URL for local development
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/dbname")
if not SQLALCHEMY_DATABASE_URL:
    raise ValueError(f"Could not load .env at {env_path}")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def initialize_vector_extension():
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()
