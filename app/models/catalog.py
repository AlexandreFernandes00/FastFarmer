import uuid
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.types import JSON
from ..database import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(PGUUID(as_uuid=True), primary_key=True,
                default=uuid.uuid4, server_default=text("uuid_generate_v4()"))
    type = Column(String, nullable=False)  # 'equipment' | 'service'
    name = Column(String, nullable=False)
    attributes_schema = Column(JSON)       # keep JSONB in DB; SQLAlchemy JSON is fine
    parent_id = Column(PGUUID(as_uuid=True), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)

class Service(Base):
    __tablename__ = "services"

    id = Column(PGUUID(as_uuid=True), primary_key=True,
                default=uuid.uuid4, server_default=text("uuid_generate_v4()"))
    provider_id = Column(PGUUID(as_uuid=True), ForeignKey("provider_profiles.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(PGUUID(as_uuid=True), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    description = Column(Text)
    capabilities = Column(JSON)  # later: dict of capabilities
    lead_time_days = Column(String)  # keep simple for now; or Integer
    status = Column(String, nullable=False, server_default=text("'active'"))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
