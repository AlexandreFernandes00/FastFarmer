from uuid import UUID
from pydantic import BaseModel, ConfigDict

class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    type: str
    name: str
