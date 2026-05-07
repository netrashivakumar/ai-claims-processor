from pydantic import BaseModel
from typing import List, Optional

class DocumentBase(BaseModel):
    filename: str
    file_type: str

class Document(DocumentBase):
    id: int
    class Config:
        from_attributes = True

class ClaimBase(BaseModel):
    policy_number: str
    claim_details: str

class ClaimCreate(ClaimBase):
    pass

class Claim(ClaimBase):
    id: int
    status: str
    documents: List[Document] = []
    class Config:
        from_attributes = True


class ClaimUpdate(BaseModel):
    policy_number: Optional[str] = None
    claim_details: Optional[str] = None
    status: Optional[str] = None

class ClaimResponse(BaseModel):
    id: int
    policy_number: str
    claim_details: Optional[str]
    status: str
    
    class Config:
        from_attributes = True # This allows Pydantic to read from your Database Model


