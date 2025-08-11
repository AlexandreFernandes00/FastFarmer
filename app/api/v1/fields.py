from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from ...database import get_db
from ...dependencies.auth import require_client
from ...models.user import User
from ...models.profile import ClientProfile
from ...models.geo import Field
from ...schemas.field import FieldCreate, FieldUpdate, FieldRead

router = APIRouter()

def get_client_profile(db: Session, user_id: UUID) -> ClientProfile:
    prof = db.query(ClientProfile).filter(ClientProfile.user_id == user_id).first()
    if not prof:
        raise HTTPException(status_code=403, detail="Client profile required")
    return prof

@router.get("/", response_model=list[FieldRead])
def list_fields(db: Session = Depends(get_db), current: User = Depends(require_client)):
    prof = get_client_profile(db, current.id)
    return (
        db.query(Field)
        .filter(Field.client_id == prof.id)
        .order_by(Field.created_at.desc())
        .all()
    )

@router.post("/", response_model=FieldRead, status_code=201)
def create_field(payload: FieldCreate, db: Session = Depends(get_db), current: User = Depends(require_client)):
    prof = get_client_profile(db, current.id)
    # Minimal validation: ensure a geometry exists
    geom = payload.geojson.get("geometry") if isinstance(payload.geojson, dict) else None
    if not geom:
        raise HTTPException(status_code=400, detail="geojson.geometry is required")

    f = Field(
        client_id=prof.id,
        name=payload.name,
        geojson=payload.geojson,
        area_ha=payload.area_ha,
        centroid=payload.centroid
    )
    db.add(f); db.commit(); db.refresh(f)
    return f

@router.put("/{field_id}", response_model=FieldRead)
def update_field(field_id: UUID, payload: FieldUpdate, db: Session = Depends(get_db), current: User = Depends(require_client)):
    prof = get_client_profile(db, current.id)
    f = db.query(Field).filter(Field.id == field_id, Field.client_id == prof.id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Field not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(f, k, v)
    db.add(f); db.commit(); db.refresh(f)
    return f

@router.delete("/{field_id}", status_code=204)
def delete_field(field_id: UUID, db: Session = Depends(get_db), current: User = Depends(require_client)):
    prof = get_client_profile(db, current.id)
    f = db.query(Field).filter(Field.id == field_id, Field.client_id == prof.id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Field not found")
    db.delete(f); db.commit()
