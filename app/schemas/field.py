from uuid import UUID
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, field_validator

class FieldCreate(BaseModel):
    name: str
    geojson: Dict[str, Any]
    area_ha: float
    centroid: Optional[Dict[str, Any]] = None

    @field_validator("area_ha")
    @classmethod
    def nonneg(cls, v): 
        if v <= 0: raise ValueError("area_ha must be > 0")
        return v

class FieldUpdate(BaseModel):
    name: Optional[str] = None

class FieldRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    client_id: UUID
    name: str
    geojson: Dict[str, Any]
    area_ha: float
    centroid: Optional[Dict[str, Any]] = None
