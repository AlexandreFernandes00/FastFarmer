from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from ...database import get_db
from ...models.inventory import Machine
from ...models.profile import ProviderProfile
from ...schemas.machine import MachineCreate, MachineUpdate, MachineRead
from ...dependencies.auth import require_provider
from ...models.user import User

router = APIRouter()

def get_provider_profile(db: Session, user_id: UUID) -> ProviderProfile:
    prof = db.query(ProviderProfile).filter(ProviderProfile.user_id == user_id).first()
    if not prof:
        raise HTTPException(status_code=403, detail="Provider profile required")
    return prof

@router.get("/", response_model=list[MachineRead])
def list_my_machines(db: Session = Depends(get_db), current: User = Depends(require_provider)):
    prof = get_provider_profile(db, current.id)
    return db.query(Machine).filter(Machine.provider_id == prof.id).all()

@router.post("/", response_model=MachineRead, status_code=201)
def create_machine(payload: MachineCreate, db: Session = Depends(get_db), current: User = Depends(require_provider)):
    prof = get_provider_profile(db, current.id)
    m = Machine(provider_id=prof.id, **payload.model_dump(exclude_unset=True))
    db.add(m)
    db.commit()
    db.refresh(m)
    return m

@router.get("/{machine_id}", response_model=MachineRead)
def get_machine(machine_id: UUID, db: Session = Depends(get_db), current: User = Depends(require_provider)):
    prof = get_provider_profile(db, current.id)
    m = db.query(Machine).filter(Machine.id == machine_id, Machine.provider_id == prof.id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Machine not found")
    return m

@router.put("/{machine_id}", response_model=MachineRead)
def update_machine(machine_id: UUID, payload: MachineUpdate, db: Session = Depends(get_db), current: User = Depends(require_provider)):
    prof = get_provider_profile(db, current.id)
    m = db.query(Machine).filter(Machine.id == machine_id, Machine.provider_id == prof.id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Machine not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(m, k, v)
    db.add(m)
    db.commit()
    db.refresh(m)
    return m

@router.delete("/{machine_id}", status_code=204)
def delete_machine(machine_id: UUID, db: Session = Depends(get_db), current: User = Depends(require_provider)):
    prof = get_provider_profile(db, current.id)
    m = db.query(Machine).filter(Machine.id == machine_id, Machine.provider_id == prof.id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Machine not found")
    db.delete(m)
    db.commit()
