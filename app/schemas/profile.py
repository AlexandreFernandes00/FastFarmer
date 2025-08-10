from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, conint, condecimal

# ----- Client -----
class ClientProfileCreate(BaseModel):
    # nothing required yet; placeholder for future fields
    pass

class ClientProfileUpdate(BaseModel):
    # add future editable fields here
    pass

class ClientProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    user_id: UUID
    rating_avg: Optional[condecimal(max_digits=3, decimal_places=2)] = None
    rating_count: int

# ----- Provider -----
class ProviderProfileCreate(BaseModel):
    business_name: Optional[str] = None
    tax_id: Optional[str] = None
    service_radius_km: Optional[condecimal(max_digits=6, decimal_places=2)] = None

class ProviderProfileUpdate(BaseModel):
    business_name: Optional[str] = None
    tax_id: Optional[str] = None
    service_radius_km: Optional[condecimal(max_digits=6, decimal_places=2)] = None

class ProviderProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    user_id: UUID
    business_name: Optional[str] = None
    tax_id: Optional[str] = None
    verification_status: Optional[str] = None
    service_radius_km: Optional[condecimal(max_digits=6, decimal_places=2)] = None
    rating_avg: Optional[condecimal(max_digits=3, decimal_places=2)] = None
    rating_count: int
