from typing import Optional
from uuid import UUID
from enum import Enum
from pydantic import BaseModel, EmailStr, constr, ConfigDict
from typing import Optional



class CustomerType(str, Enum):
    client = "client"
    provider = "provider"
    both = "both"

# Keep this name for compatibility with your routes
class UserRegister(BaseModel):
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    password: constr(min_length=8)
    customer_type: CustomerType

class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    is_client: bool
    is_provider: bool
    is_admin: bool


class UserUpdateMe(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
