from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field

# ---- Shared base ----
class PricingBase(BaseModel):
    owner_type: str = Field(..., description="Type of owner: 'listing' or 'machine'")
    owner_id: UUID
    unit: str = Field(..., description="Unit type: 'hour', 'ha', 'km', etc.")
    base_price: float
    min_qty: Optional[float] = None
    transport_flat_fee: Optional[float] = None
    transport_per_km: Optional[float] = None
    currency: Optional[str] = Field(default="EUR", max_length=3)
    surcharges: Optional[Dict[str, Any]] = None


# ---- For creating ----
class PricingCreate(PricingBase):
    pass


# ---- For updating ----
class PricingUpdate(BaseModel):
    unit: Optional[str] = None
    base_price: Optional[float] = None
    min_qty: Optional[float] = None
    transport_flat_fee: Optional[float] = None
    transport_per_km: Optional[float] = None
    currency: Optional[str] = None
    surcharges: Optional[Dict[str, Any]] = None


# ---- For reading ----
class PricingRead(PricingBase):
    id: UUID

    class Config:
        from_attributes = True  # allows reading from SQLAlchemy models
