# app/models/pricing_rule.py
import uuid
from sqlalchemy import Column, String, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database import Base

class PricingRule(Base):
    __tablename__ = "pricing_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_type = Column(String, nullable=False)          # "listing" | "machine"
    owner_id = Column(UUID(as_uuid=True), nullable=False)
    unit = Column(String, nullable=False)                # "hour" | "hectare" | "km" | "job"
    base_price = Column(Float, nullable=False)
    min_qty = Column(Float)
    transport_flat_fee = Column(Float)
    transport_per_km = Column(Float)
    currency = Column(String(3))                         # may be NULL; default later
    surcharges = Column(JSONB)
