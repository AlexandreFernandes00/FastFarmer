from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, condecimal

class PricingCreate(BaseModel):
    owner_type: str  # 'machine' | 'service'
    owner_id: UUID
    unit: str        # 'hour' | 'hectare' | 'km' | 'job'
    base_price: condecimal(max_digits=12, decimal_places=2)
    min_qty: Optional[condecimal(max_digits=12, decimal_places=2)] = None
    transport_flat_fee: Optional[condecimal(max_digits=12, decimal_places=2)] = None
    transport_per_km: Optional[condecimal(max_digits=12, decimal_places=3)] = None
    surcharges: Optional[str] = None
    currency: Optional[str] = "EUR"

class PricingUpdate(BaseModel):
    unit: Optional[str] = None
    base_price: Optional[condecimal(max_digits=12, decimal_places=2)] = None
    min_qty: Optional[condecimal(max_digits=12, decimal_places=2)] = None
    transport_flat_fee: Optional[condecimal(max_digits=12, decimal_places=2)] = None
    transport_per_km: Optional[condecimal(max_digits=12, decimal_places=3)] = None
    surcharges: Optional[str] = None
    currency: Optional[str] = None

class PricingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    owner_type: str
    owner_id: UUID
    unit: str
    base_price: float
    min_qty: Optional[float] = None
    transport_flat_fee: Optional[float] = None
    transport_per_km: Optional[float] = None
    surcharges: Optional[str] = None
    currency: str
