from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from .database import Base

class Claim(Base):
    __tablename__ = "claims"

    id = Column(Integer, primary_key=True, index=True)
    policy_number = Column(String, index=True)
    claim_details = Column(Text)
    status = Column(String, default="Pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship to the chunks
    chunks = relationship("DocumentChunk", back_populates="claim")

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(Integer, ForeignKey("claims.id"))
    content = Column(Text, nullable=False)
    
    # 384 dimensions for the local HuggingFace model (all-MiniLM-L6-v2)
    embedding = Column(Vector(384))

    claim = relationship("Claim", back_populates="chunks")
