import uuid
from sqlalchemy import Column, String, Integer, Numeric, DateTime, Boolean, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from ..database import Base

class ClientProfile(Base):
    __tablename__ = "client_profiles"

    id = Column(PGUUID(as_uuid=True), primary_key=True,
                default=uuid.uuid4, server_default=text("uuid_generate_v4()"))
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)

    # Ratings (maintained by reviews later)
    rating_avg = Column(Numeric(3, 2), server_default=text("0"))
    rating_count = Column(Integer, nullable=False, server_default=text("0"))

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))


class ProviderProfile(Base):
    __tablename__ = "provider_profiles"

    id = Column(PGUUID(as_uuid=True), primary_key=True,
                default=uuid.uuid4, server_default=text("uuid_generate_v4()"))
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)

    business_name = Column(String)
    tax_id = Column(String)
    verification_status = Column(String, server_default=text("'submitted'"))
    service_radius_km = Column(Numeric(6, 2), server_default=text("50"))

    rating_avg = Column(Numeric(3, 2), server_default=text("0"))
    rating_count = Column(Integer, nullable=False, server_default=text("0"))

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
