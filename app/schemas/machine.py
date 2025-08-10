from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, conint, condecimal

class MachineCreate(BaseModel):
    make: str
    model: str
    year: Optional[conint(ge=1950, le=2100)] = None
    category_id: Optional[UUID] = None
    serial_no: Optional[str] = None
    power_hp: Optional[condecimal(max_digits=6, decimal_places=2)] = None
    power_kw: Optional[condecimal(max_digits=6, decimal_places=2)] = None
    working_width_m: Optional[condecimal(max_digits=6, decimal_places=2)] = None
    capacity_per_hour: Optional[condecimal(max_digits=10, decimal_places=2)] = None
    pto_hp: Optional[condecimal(max_digits=6, decimal_places=2)] = None
    is_road_legal: Optional[bool] = None
    transport_width_m: Optional[condecimal(max_digits=6, decimal_places=2)] = None
    tire_size: Optional[str] = None
    fuel_type: Optional[str] = None
    hours_meter: Optional[condecimal(max_digits=10, decimal_places=2)] = None
    telemetry_enabled: Optional[bool] = None
    notes: Optional[str] = None

class MachineUpdate(MachineCreate):
    status: Optional[str] = None  # 'active'|'paused'|'retired'

class MachineRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    provider_id: UUID
    category_id: Optional[UUID] = None
    make: str
    model: str
    year: Optional[int] = None
    serial_no: Optional[str] = None
    power_hp: Optional[float] = None
    power_kw: Optional[float] = None
    working_width_m: Optional[float] = None
    capacity_per_hour: Optional[float] = None
    pto_hp: Optional[float] = None
    is_road_legal: Optional[bool] = None
    transport_width_m: Optional[float] = None
    tire_size: Optional[str] = None
    fuel_type: Optional[str] = None
    hours_meter: Optional[float] = None
    telemetry_enabled: Optional[bool] = None
    notes: Optional[str] = None
    status: str
