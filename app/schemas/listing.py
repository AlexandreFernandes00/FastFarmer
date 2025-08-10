from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, condecimal

class ListingCreate(BaseModel):
    type: str  # 'machine' (service later)
    ref_machine_id: UUID
    title: str
    description: Optional[str] = None
    max_distance_km: Optional[condecimal(max_digits=6, decimal_places=2)] = None

class ListingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None  # 'active'|'paused'|'archived'
    max_distance_km: Optional[condecimal(max_digits=6, decimal_places=2)] = None

class ListingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    provider_id: UUID
    type: str
    ref_machine_id: Optional[UUID] = None
    title: str
    description: Optional[str] = None
    status: str
    max_distance_km: Optional[float] = None
