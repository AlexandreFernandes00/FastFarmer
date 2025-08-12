from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, field_validator

ALLOWED_UNITS = {"hour", "hectare", "km", "job"}

class PricingBase(BaseModel):
    listing_id: Optional[UUID] = None
    unit: Optional[str] = Field(None, description="hour | hectare | km | job")
    base_price: Optional[float] = None
    min_qty: Optional[float] = None
    transport_flat_fee: Optional[float] = None
    transport_per_km: Optional[float] = None
    currency: Optional[str] = Field(default="EUR", max_length=3)
    surcharges: Optional[Dict[str, Any]] = None

    @field_validator("unit")
    @classmethod
    def validate_unit(cls, v):
        if v is None:
            return v
        if v not in ALLOWED_UNITS:
            raise ValueError(f"unit must be one of {sorted(ALLOWED_UNITS)}")
        return v

    @field_validator("base_price", "min_qty", "transport_flat_fee", "transport_per_km")
    @classmethod
    def validate_nonnegative(cls, v):
        if v is None:
            return v
        if v < 0:
            raise ValueError("numeric values must be >= 0")
        return v


class PricingCreate(PricingBase):
    listing_id: UUID
    unit: str
    base_price: float


class PricingPut(BaseModel):
    """Full replace: all main fields required."""
    listing_id: UUID
    unit: str
    base_price: float
    min_qty: Optional[float] = None
    transport_flat_fee: Optional[float] = None
    transport_per_km: Optional[float] = None
    currency: Optional[str] = Field(default="EUR", max_length=3)
    surcharges: Optional[Dict[str, Any]] = None

    @field_validator("unit")
    @classmethod
    def validate_unit(cls, v):
        if v not in ALLOWED_UNITS:
            raise ValueError(f"unit must be one of {sorted(ALLOWED_UNITS)}")
        return v

    @field_validator("base_price", "min_qty", "transport_flat_fee", "transport_per_km")
    @classmethod
    def validate_nonnegative(cls, v):
        if v is None:
            return v
        if v < 0:
            raise ValueError("numeric values must be >= 0")
        return v


class PricingUpdate(PricingBase):
    """Partial update: send only fields to change."""
    pass


class PricingRead(BaseModel):
    id: UUID
    listing_id: UUID
    unit: str
    base_price: float
    min_qty: Optional[float] = None
    transport_flat_fee: Optional[float] = None
    transport_per_km: Optional[float] = None
    currency: Optional[str] = Field(default="EUR", max_length=3)
    surcharges: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True
