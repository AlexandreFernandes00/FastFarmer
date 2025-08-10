from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from ...database import get_db
from ...models.user import User
from ...models.profile import ClientProfile, ProviderProfile
from ...schemas.profile import (
    ClientProfileCreate, ClientProfileUpdate, ClientProfileRead,
    ProviderProfileCreate, ProviderProfileUpdate, ProviderProfileRead
)
from ...schemas.user import UserRead, UserUpdateMe
from ...dependencies.auth import get_current_user, require_client, require_provider

router = APIRouter()

# ----- Me -----
@router.get("/me", response_model=UserRead)
def me(current: User = Depends(get_current_user)):
    return current

@router.put("/me", response_model=UserRead)
def update_me(payload: UserUpdateMe, db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    if payload.full_name:
        current.full_name = payload.full_name.strip()
    if payload.phone is not None:
        current.phone = payload.phone.strip() if payload.phone else None
    db.add(current)
    db.commit()
    db.refresh(current)
    return current

# ----- Client profile -----
@router.get("/me/client-profile", response_model=ClientProfileRead)
def get_client_profile(db: Session = Depends(get_db), current: User = Depends(require_client)):
    prof = db.query(ClientProfile).filter(ClientProfile.user_id == current.id).first()
    if not prof:
        raise HTTPException(status_code=404, detail="Client profile not found")
    return prof

@router.post("/me/client-profile", response_model=ClientProfileRead, status_code=201)
def create_client_profile(_: ClientProfileCreate, db: Session = Depends(get_db), current: User = Depends(require_client)):
    existing = db.query(ClientProfile).filter(ClientProfile.user_id == current.id).first()
    if existing:
        return existing
    prof = ClientProfile(user_id=current.id)
    db.add(prof)
    db.commit()
    db.refresh(prof)
    return prof

@router.put("/me/client-profile", response_model=ClientProfileRead)
def update_client_profile(_: ClientProfileUpdate, db: Session = Depends(get_db), current: User = Depends(require_client)):
    prof = db.query(ClientProfile).filter(ClientProfile.user_id == current.id).first()
    if not prof:
        raise HTTPException(status_code=404, detail="Client profile not found")
    # add future editable fields here
    db.add(prof)
    db.commit()
    db.refresh(prof)
    return prof

# ----- Provider profile -----
@router.get("/me/provider-profile", response_model=ProviderProfileRead)
def get_provider_profile(db: Session = Depends(get_db), current: User = Depends(require_provider)):
    prof = db.query(ProviderProfile).filter(ProviderProfile.user_id == current.id).first()
    if not prof:
        raise HTTPException(status_code=404, detail="Provider profile not found")
    return prof

@router.post("/me/provider-profile", response_model=ProviderProfileRead, status_code=201)
def create_provider_profile(payload: ProviderProfileCreate, db: Session = Depends(get_db), current: User = Depends(require_provider)):
    existing = db.query(ProviderProfile).filter(ProviderProfile.user_id == current.id).first()
    if existing:
        return existing
    prof = ProviderProfile(
        user_id=current.id,
        business_name=(payload.business_name or None),
        tax_id=(payload.tax_id or None),
        service_radius_km=payload.service_radius_km
    )
    db.add(prof)
    db.commit()
    db.refresh(prof)
    return prof

@router.put("/me/provider-profile", response_model=ProviderProfileRead)
def update_provider_profile(payload: ProviderProfileUpdate, db: Session = Depends(get_db), current: User = Depends(require_provider)):
    prof = db.query(ProviderProfile).filter(ProviderProfile.user_id == current.id).first()
    if not prof:
        raise HTTPException(status_code=404, detail="Provider profile not found")

    if payload.business_name is not None:
        prof.business_name = payload.business_name or None
    if payload.tax_id is not None:
        prof.tax_id = payload.tax_id or None
    if payload.service_radius_km is not None:
        prof.service_radius_km = payload.service_radius_km

    db.add(prof)
    db.commit()
    db.refresh(prof)
    return prof
