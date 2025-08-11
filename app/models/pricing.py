from sqlalchemy import Column, String, Float, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.database import Base

class Pricing(Base):
    __tablename__ = "pricing"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_type = Column(String, nullable=False)  # "listing" or "machine"
    owner_id = Column(UUID(as_uuid=True), nullable=False)
    unit = Column(String, nullable=False)
    base_price = Column(Float, nullable=False)
    min_qty = Column(Float)
    transport_flat_fee = Column(Float)
    transport_per_km = Column(Float)
    currency = Column(String(3), default="EUR")
    surcharges = Column(JSON)  # JSONB column
