# app/schemas/quotes.py
from uuid import UUID
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, conlist, condecimal

class QuoteItemIn(BaseModel):
    kind: Literal["base","transport_km","surcharge","misc"] = "base"
    description: str
    unit: Optional[str] = None
    qty: Optional[condecimal(max_digits=12, decimal_places=2)] = None
    unit_price: Optional[condecimal(max_digits=12, decimal_places=2)] = None
    line_total: condecimal(max_digits=12, decimal_places=2)

class QuoteCreate(BaseModel):
    request_id: UUID
    currency: str = Field(default="EUR", min_length=3, max_length=3)
    message: Optional[str] = None
    items: conlist(QuoteItemIn, min_length=1)
    transport_fee: Optional[condecimal(max_digits=12, decimal_places=2)] = None
    surcharges: Optional[dict] = None
    expires_at: Optional[str] = None  # ISO string

class QuoteRead(BaseModel):
    id: UUID
    request_id: UUID
    provider_id: UUID
    currency: str
    subtotal: float
    transport_fee: Optional[float] = None
    surcharges: Optional[dict] = None
    total: float
    status: str
    expires_at: Optional[str] = None
    items: list[QuoteItemIn] = []
    message: Optional[str] = None

    class Config:
        from_attributes = True
