from pydantic import BaseModel
from typing import Optional

class QueryRequest(BaseModel):
    question: str

class SourceCitation(BaseModel):
    document: str
    revision: Optional[str] = None
    page: int

class QueryResponse(BaseModel):
    status: str
    natural_response: Optional[str] = None
    answer: Optional[str] = None
    product: Optional[str] = None
    specification: Optional[str] = None
    source: Optional[SourceCitation] = None
    evidence: Optional[str] = None
    confidence: Optional[float] = None
    message: Optional[str] = None