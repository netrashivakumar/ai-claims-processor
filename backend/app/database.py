import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine,text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import List, Dict, Any
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

# 2. CALL the function right here
# This ensures it runs as soon as the database.py is imported
initialize_vector_extension()

def fetch_claims_with_chunks_structured(db_session) -> List[Dict[str, Any]]:
    # 1. Ask Postgres to describe what columns actually exist on document_chunks
    col_check = db_session.execute(text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'document_chunks';
    """))
    existing_cols = [r[0] for r in col_check.fetchall()]
    
    # 2. Automatically find your text content column and status column variations
    text_col = next((c for c in existing_cols if c in ['content', 'text', 'chunk_text', 'chunk']), 'id')
    status_col = next((c for c in existing_cols if c in ['status', 'embedding_status', 'state']), 'id')
    
    # 3. Construct a safe SQL query using your actual verified columns
    query_str = f"""
        SELECT 
            c.id AS claim_id, 
            c.policy_number, 
            c.claim_details, 
            c.status,
            d.id AS doc_id, 
            d.{text_col} AS filename,  
            d.{status_col} AS file_type    
        FROM claims c
        LEFT JOIN document_chunks d ON c.id = d.claim_id
        ORDER BY c.id DESC;
    """
    
    result = db_session.execute(text(query_str))
    rows = result.mappings().all()
    
    claims_map: Dict[int, Dict[str, Any]] = {}
    
    for row in rows:
        claim_id = row['claim_id']
        
        if claim_id not in claims_map:
            claims_map[claim_id] = {
                "id": claim_id,
                "policy_number": row['policy_number'],
                "claim_details": row['claim_details'],
                "status": row['status'],
                "documents": []
            }
        
        if row['doc_id'] is not None:
            # Map values back to your exact Pydantic format safely
            document_data = {
                "id": row['doc_id'],
                "filename": str(row['filename']) if row['filename'] else "Empty",
                "file_type": str(row['file_type']) if row['file_type'] else "PENDING"
            }
            if document_data not in claims_map[claim_id]["documents"]:
                claims_map[claim_id]["documents"].append(document_data)
                
    return list(claims_map.values())

