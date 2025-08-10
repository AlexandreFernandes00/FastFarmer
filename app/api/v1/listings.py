from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from ...database import get_db
from ...models.inventory import Listing, Machine
from ...models.profile import ProviderProfile
from ...schemas.listing import ListingCreate, ListingUpdate, ListingRead
from ...dependencies.auth import require_provider
from ...models.user import User

router = APIRouter()

def get_provider_profile(db: Session, user_id: UUID) -> ProviderProfile:
    prof = db.query(ProviderProfile).filter(ProviderProfile.user_id == user_id).first()
    if not prof:
        raise HTTPException(status_code=403, detail="Provider profile required")
    return prof

@router.get("/", response_model=list[ListingRead])
def list_my_listings(db: Session = Depends(get_db), current: User = Depends(require_provider)):
    prof = get_provider_profile(db, current.id)
    return db.query(Listing).filter(Listing.provider_id == prof.id).all()

@router.post("/", response_model=ListingRead, status_code=201)
def create_listing(payload: ListingCreate, db: Session = Depends(get_db), current: User = Depends(require_provider)):
    prof = get_provider_profile(db, current.id)

    if payload.type != "machine":
        raise HTTPException(status_code=400, detail="Only machine listings supported in v0.1")
    # ownership check
    machine = db.query(Machine).filter(Machine.id == payload.ref_machine_id, Machine.provider_id == prof.id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found or not yours")

    lst = Listing(
        type="machine",
        ref_machine_id=payload.ref_machine_id,
        provider_id=prof.id,
        title=payload.title,
        description=payload.description,
        max_distance_km=payload.max_distance_km
    )
    db.add(lst)
    db.commit()
    db.refresh(lst)
    return lst

@router.put("/{listing_id}", response_model=ListingRead)
def update_listing(listing_id: UUID, payload: ListingUpdate, db: Session = Depends(get_db), current: User = Depends(require_provider)):
    prof = get_provider_profile(db, current.id)
    lst = db.query(Listing).filter(Listing.id == listing_id, Listing.provider_id == prof.id).first()
    if not lst:
        raise HTTPException(status_code=404, detail="Listing not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(lst, k, v)
    db.add(lst)
    db.commit()
    db.refresh(lst)
    return lst

@router.delete("/{listing_id}", status_code=204)
def delete_listing(listing_id: UUID, db: Session = Depends(get_db), current: User = Depends(require_provider)):
    prof = get_provider_profile(db, current.id)
    lst = db.query(Listing).filter(Listing.id == listing_id, Listing.provider_id == prof.id).first()
    if not lst:
        raise HTTPException(status_code=404, detail="Listing not found")
    db.delete(lst)
    db.commit()
