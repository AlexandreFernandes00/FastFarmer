import uuid
from sqlalchemy import Column, String, Boolean, DateTime, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from ..database import Base


class User(Base):
    __tablename__ = "users"

    # UUID primary key
    id = Column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,                    # app-side default
        server_default=text("uuid_generate_v4()")  # db-side default (if extension enabled)
    )

    # Core fields
    email = Column(String, unique=True, nullable=False, index=True)
    full_name = Column(String, nullable=False)
    phone = Column(String)

    # Auth
    password_hash = Column(String, nullable=False)

    # Roles
    is_client = Column(Boolean, nullable=False, default=True, server_default=text("true"))
    is_provider = Column(Boolean, nullable=False, default=False, server_default=text("false"))
    is_admin = Column(Boolean, nullable=False, default=False, server_default=text("false"))

    # Timestamps (match schema defaults)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=text("now()"))
