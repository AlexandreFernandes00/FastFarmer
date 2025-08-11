from uuid import UUID
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class QuoteCreate(BaseModel):
    request_id: UUID
    total_estimate: float
    breakdown: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    expires_at: Optional[datetime] = None

class QuoteUpdate(BaseModel):
    total_estimate: Optional[float] = None
    breakdown: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    status: Optional[str] = None    # provider can withdraw; client will accept via another endpoint later

class QuoteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    request_id: UUID
    provider_id: UUID
    total_estimate: float
    breakdown: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    expires_at: Optional[datetime] = None
    status: str
