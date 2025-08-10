import uuid
from sqlalchemy import Column, String, Integer, Numeric, Boolean, DateTime, ForeignKey, Text, CheckConstraint, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from ..database import Base

class Machine(Base):
    __tablename__ = "machines"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("uuid_generate_v4()"))
    provider_id = Column(PGUUID(as_uuid=True), ForeignKey("provider_profiles.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(PGUUID(as_uuid=True), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)

    make = Column(String, nullable=False)
    model = Column(String, nullable=False)
    year = Column(Integer)
    serial_no = Column(String)

    power_hp = Column(Numeric(6,2))
    power_kw = Column(Numeric(6,2))
    working_width_m = Column(Numeric(6,2))
    capacity_per_hour = Column(Numeric(10,2))
    pto_hp = Column(Numeric(6,2))
    is_road_legal = Column(Boolean, server_default=text("false"))
    transport_width_m = Column(Numeric(6,2))
    tire_size = Column(String)
    fuel_type = Column(String)
    hours_meter = Column(Numeric(10,2), server_default=text("0"))
    telemetry_enabled = Column(Boolean, server_default=text("false"))
    notes = Column(Text)
    status = Column(String, nullable=False, server_default=text("'active'"))

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))

    __table_args__ = (
        CheckConstraint("status IN ('active','paused','retired')", name="machines_status_ck"),
    )


class Listing(Base):
    __tablename__ = "listings"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("uuid_generate_v4()"))
    type = Column(String, nullable=False)  # 'machine' | 'service'
    ref_machine_id = Column(PGUUID(as_uuid=True), ForeignKey("machines.id", ondelete="CASCADE"), nullable=True)
    ref_service_id = Column(PGUUID(as_uuid=True), ForeignKey("services.id", ondelete="CASCADE"), nullable=True)
    provider_id = Column(PGUUID(as_uuid=True), ForeignKey("provider_profiles.id", ondelete="CASCADE"), nullable=False)

    title = Column(Text, nullable=False)
    description = Column(Text)
    status = Column(String, nullable=False, server_default=text("'active'"))
    max_distance_km = Column(Numeric(6,2))

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))

    __table_args__ = (
        CheckConstraint("status IN ('active','paused','archived')", name="listings_status_ck"),
    )


class PricingRule(Base):
    __tablename__ = "pricing_rules"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("uuid_generate_v4()"))
    owner_type = Column(String, nullable=False)  # 'machine' | 'service'
    owner_id = Column(PGUUID(as_uuid=True), nullable=False)

    unit = Column(String, nullable=False)  # 'hour' | 'hectare' | 'km' | 'job'
    base_price = Column(Numeric(12,2), nullable=False)
    min_qty = Column(Numeric(12,2), server_default=text("0"))
    transport_flat_fee = Column(Numeric(12,2), server_default=text("0"))
    transport_per_km = Column(Numeric(12,3), server_default=text("0"))
    surcharges = Column(Text)  # keep JSON later; Text here to avoid driver JSON diffs
    currency = Column(String, nullable=False, server_default=text("'EUR'"))
