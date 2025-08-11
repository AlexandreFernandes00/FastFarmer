import uuid
from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from ..database import Base

class Field(Base):
    __tablename__ = "fields"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("uuid_generate_v4()"))
    client_id = Column(PGUUID(as_uuid=True), ForeignKey("client_profiles.id", ondelete="CASCADE"), nullable=False)

    name = Column(String, nullable=False)
    geojson = Column(JSONB, nullable=False)          # full Feature or just geometry; we’re sending Feature
    area_ha = Column(Numeric(12, 4), nullable=False) # cached area in hectares (frontend or server)
    centroid = Column(JSONB, nullable=True)          # GeoJSON Point

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))