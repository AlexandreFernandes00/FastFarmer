from sqlalchemy import Column, String, Boolean, Integer
from ..database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False, index=True)
    full_name = Column(String, nullable=False)
    is_client = Column(Boolean, default=True)
    is_provider = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
