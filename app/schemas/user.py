from typing import Optional
from uuid import UUID
from enum import Enum
from pydantic import BaseModel, EmailStr, constr, ConfigDict


class CustomerType(str, Enum):
    client = "client"
    provider = "provider"
    both = "both"


# Public registration payload (no admin flag here)
class UserRegister(BaseModel):
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    password: constr(min_length=8)
    customer_type: CustomerType


# Public response shape
class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    is_client: bool
    is_provider: bool
    is_admin: bool  # will always be False from public register
