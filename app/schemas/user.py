from pydantic import BaseModel, EmailStr, constr
from enum import Enum

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    is_client: bool = True
    is_provider: bool = False
    is_admin: bool = False

class UserCreate(UserBase):
    pass

class CustomerType(str, Enum):
    client = "client"
    provider = "provider"
    both = "both"

class UserRegister(BaseModel):
    email: EmailStr
    full_name: str
    phone: str | None = None
    password: constr(min_length=8)  # basic server-side length check
    customer_type: CustomerType

class UserRead(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    phone: str | None = None
    is_client: bool
    is_provider: bool
    is_admin: bool

    class Config:
        orm_mode = True