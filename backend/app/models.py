from .database import Base
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime


class Claim(Base):
    __tablename__ = "claims"

    id = Column(Integer, primary_key=True, index=True)
    policy_number = Column(String, unique=True, index=True, nullable=False)
    claim_details = Column(Text, nullable=True)
    status = Column(String, default="pending")  # e.g., pending, processing, completed
    # status = Column(String, nullable=True)  # e.g., pending, processing, completed
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship to documents
    documents = relationship("Document", back_populates="claim")

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    claim_id = Column(Integer, ForeignKey("claims.id"))
    
    # Relationship back to the claim
    claim = relationship("Claim", back_populates="documents")
