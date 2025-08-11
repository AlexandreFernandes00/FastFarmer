from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID

class PricingBase(BaseModel):
    owner_type: str
    owner_id: UUID
    unit: str
    base_price: float
    min_qty: Optional[float] = None
    transport_flat_fee: Optional[float] = None
    transport_per_km: Optional[float] = None
    currency: Optional[str] = Field(default="EUR", max_length=3)
    surcharges: Optional[Dict[str, Any]] = None  # JSONB column

class PricingCreate(PricingBase):
    pass

class PricingUpdate(BaseModel):
    unit: Optional[str] = None
    base_price: Optional[float] = None
    min_qty: Optional[float] = None
    transport_flat_fee: Optional[float] = None
    transport_per_km: Optional[float] = None
    currency: Optional[str] = None
    surcharges: Optional[Dict[str, Any]] = None

class PricingRead(PricingBase):  # <- renamed from PricingOut
    id: UUID

    class Config:
        from_attributes = True
