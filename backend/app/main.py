from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from . import models, schemas, database
from .database import engine, SessionLocal

# Create DB tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Claims Processor")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "AI Claims Processor Backend is Running"}

@app.post("/claims/", response_model=schemas.Claim)
def create_claim(claim: schemas.ClaimCreate, db: Session = Depends(get_db)):
    db_claim = models.Claim(**claim.model_dump())
    db.add(db_claim)
    db.commit()
    db.refresh(db_claim)
    return db_claim

# The URL will look like: /claims/1
@app.put("/claims/{id}") 
def update_claim(id: int, updated_data: schemas.ClaimUpdate, db: Session = Depends(get_db)):
    # Here we use 'id' to find the row in the 'id' column
    db_claim = db.query(models.Claim).filter(models.Claim.id == id).first()
    
    if not db_claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    # Update logic
    update_dict = updated_data.dict(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(db_claim, key, value)

    db.commit()
    db.refresh(db_claim)
    return db_claim

# 1. GET ALL CLAIMS - Useful for your main dashboard table
@app.get("/claims/", response_model=list[schemas.ClaimResponse])
def get_all_claims(db: Session = Depends(get_db)):
    claims = db.query(models.Claim).all()
    return claims

@app.get("/claims/summary")
def get_summary(db: Session = Depends(get_db)):
    total_claims = db.query(func.count(models.Claim.id)).scalar()
    return {"total_claims": total_claims}

# 2. GET SINGLE CLAIM - Useful for clicking into a specific claim's details
@app.get("/claims/{id}", response_model=schemas.ClaimResponse)
def get_single_claim(id: int, db: Session = Depends(get_db)):
    claim = db.query(models.Claim).filter(models.Claim.id == id).first()
    
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    return claim

@app.delete("/claims/{id}")
def delete_claim(id: int, db: Session = Depends(get_db)):
    # 1. Find the claim in the database
    db_claim = db.query(models.Claim).filter(models.Claim.id == id).first()
    
    # 2. If it doesn't exist, tell the user
    if not db_claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    # 3. Delete the record and save changes
    db.delete(db_claim)
    db.commit()
    
    # 4. Return a confirmation message
    return {"message": f"Claim with ID {id} has been deleted"}




