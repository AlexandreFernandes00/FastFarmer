import uuid
import enum 
from sqlalchemy import Column, String, Text, DateTime, Numeric, ForeignKey, CheckConstraint, text, Enum as PgEnum, JSON, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import relationship
from ..database import Base
import sqlalchemy as sa

class RequestStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    in_progress = "in_progress"
    completed = "completed"
    rejected = "rejected"
    open = "open"
    quoted = "quoted"


class WorkRequest(Base):
    __tablename__ = "work_requests"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("uuid_generate_v4()"))
    client_id = Column(PGUUID(as_uuid=True), ForeignKey("client_profiles.id", ondelete="CASCADE"), nullable=False)

    listing_id = Column(PGUUID(as_uuid=True), ForeignKey("listings.id", ondelete="SET NULL"), nullable=True)
    field_id = Column(PGUUID(as_uuid=True), ForeignKey("fields.id", ondelete="CASCADE"), nullable=False)

    desired_date = Column(DateTime(timezone=True), nullable=True)
    time_window = Column(String, nullable=True)   # e.g., "morning", "afternoon", "flexible"
    notes = Column(Text, nullable=True)

    status = Column(
        PgEnum(RequestStatus, name="request_status", create_type=False),
        nullable=False,
        default=RequestStatus.pending,
    )
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))

    __table_args__ = (CheckConstraint("status IN ('open','quoted','accepted','cancelled')", name="work_requests_status_ck"),)


class Quote(Base):
    __tablename__ = "quotes"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("uuid_generate_v4()"))
    request_id = Column(PGUUID(as_uuid=True), ForeignKey("work_requests.id", ondelete="CASCADE"), nullable=False)
    provider_id = Column(PGUUID(as_uuid=True), ForeignKey("provider_profiles.id", ondelete="CASCADE"), nullable=False)

    total_estimate = Column(Numeric(12,2), nullable=False)
    breakdown = Column(JSONB, nullable=True)  # e.g., {"hour": 120, "km": 40, "transport_flat": 50}
    message = Column(Text, nullable=True)

    expires_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String, nullable=False, server_default=text("'sent'"))   # sent|withdrawn|accepted|expired

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))

    __table_args__ = (CheckConstraint("status IN ('sent','withdrawn','accepted','expired')", name="quotes_status_ck"),)


class QuoteStatus(str, enum.Enum):
    offered   = "offered"
    withdrawn = "withdrawn"
    accepted  = "accepted"
    rejected  = "rejected"
    expired   = "expired"

class Quote(Base):
    __tablename__ = "quotes"
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id = Column(PGUUID(as_uuid=True), ForeignKey("work_requests.id", ondelete="CASCADE"), nullable=False)
    provider_id = Column(PGUUID(as_uuid=True), ForeignKey("provider_profiles.id", ondelete="CASCADE"), nullable=False)

    currency = Column(String(3), nullable=False, default="EUR")
    message = Column(Text)
    subtotal = Column(Numeric(12,2), nullable=False, default=0)
    transport_fee = Column(Numeric(12,2))
    surcharges = Column(JSON)
    total = Column(Numeric(12,2), nullable=False, default=0)
    status = Column(PgEnum(QuoteStatus, name="quote_status", create_type=False), nullable=False, default=QuoteStatus.offered)
    expires_at = Column(TIMESTAMP(timezone=True))

    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()"))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()"))

    items = relationship("QuoteItem", back_populates="quote", cascade="all, delete-orphan")

class QuoteItem(Base):
    __tablename__ = "quote_items"
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quote_id = Column(PGUUID(as_uuid=True), ForeignKey("quotes.id", ondelete="CASCADE"), nullable=False)
    kind = Column(String(32), nullable=False)      # 'base','transport_km','surcharge','misc'
    description = Column(Text, nullable=False)
    unit = Column(String(24))
    qty = Column(Numeric(12,2))
    unit_price = Column(Numeric(12,2))
    line_total = Column(Numeric(12,2), nullable=False)

    quote = relationship("Quote", back_populates="items")