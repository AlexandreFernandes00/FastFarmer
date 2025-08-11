from uuid import UUID
from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class WorkRequestCreate(BaseModel):
    field_id: UUID
    listing_id: Optional[UUID] = None
    desired_date: Optional[datetime] = None
    time_window: Optional[str] = None
    notes: Optional[str] = None

class WorkRequestUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None

class WorkRequestRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    client_id: UUID
    field_id: UUID
    listing_id: Optional[UUID] = None
    desired_date: Optional[datetime] = None
    time_window: Optional[str] = None
    notes: Optional[str] = None
    status: str
