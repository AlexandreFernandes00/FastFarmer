# app/api/v1/listings.py
from __future__ import annotations

from typing import List, Optional
from uuid import UUID

import sqlalchemy as sa
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ...database import get_db
from ...dependencies.auth import require_provider
from ...models.inventory import Listing  # adjust if your model lives elsewhere
from ...models.profile import ProviderProfile
from ...models.user import User

router = APIRouter()


# --------- Pydantic payloads (lightweight, local to this router) ---------
class ListingCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    ref_machine_id: Optional[UUID] = None
    status: Optional[str] = None  # defaults to active in DB or via code


class ListingUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    ref_machine_id: Optional[UUID] = None
    status: Optional[str] = None  # active|paused|retired, etc.


# --------- Helpers ---------
def get_provider_profile(db: Session, user_id: UUID) -> ProviderProfile:
    prof = (
        db.query(ProviderProfile)
        .filter(ProviderProfile.user_id == user_id)
        .first()
    )
    if not prof:
        raise HTTPException(status_code=403, detail="Provider profile required")
    return prof


def shape_listing(l: Listing) -> dict:
    """Minimal shape the frontend expects."""
    return {
        "id": str(l.id),
        "title": l.title or "",
        "description": l.description or "",
        "status": (l.status or "active"),
        # many schemas call this machine_id; marketplace expects ref_machine_id
        "ref_machine_id": str(getattr(l, "ref_machine_id", "")) if getattr(l, "ref_machine_id", None) else None,
        "created_at": getattr(l, "created_at", None),
        "updated_at": getattr(l, "updated_at", None),
    }


# --------- PUBLIC READ (used by marketplace.html) ---------
@router.get("/public")
def public_listings(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(None, description="Search in title/description"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> List[dict]:
    stmt = sa.select(Listing).where(
        sa.or_(Listing.status == "active", Listing.status.is_(None))
    ).order_by(Listing.created_at.desc()).limit(limit).offset(offset)

    if q:
        like = f"%{q.lower()}%"
        stmt = stmt.where(
            sa.or_(
                sa.func.lower(Listing.title).like(like),
                sa.func.lower(Listing.description).like(like),
            )
        )

    rows = db.execute(stmt).scalars().all()
    return [shape_listing(r) for r in rows]


@router.get("/public/{listing_id}")
def public_get_one(
    listing_id: UUID,
    db: Session = Depends(get_db),
) -> dict:
    l = db.get(Listing, listing_id)
    if not l or (l.status not in (None, "active")):
        raise HTTPException(status_code=404, detail="Listing not found")
    return shape_listing(l)


# --------- PROVIDER CRUD (requires provider role) ---------
@router.get("/", response_model=List[dict])
def my_listings(
    db: Session = Depends(get_db),
    current: User = Depends(require_provider),
) -> List[dict]:
    prof = get_provider_profile(db, current.id)
    rows = (
        db.query(Listing)
        .filter(Listing.provider_id == prof.id)
        .order_by(Listing.created_at.desc())
        .all()
    )
    return [shape_listing(r) for r in rows]


@router.post("/", response_model=dict, status_code=201)
def create_listing(
    payload: ListingCreate,
    db: Session = Depends(get_db),
    current: User = Depends(require_provider),
) -> dict:
    prof = get_provider_profile(db, current.id)
    l = Listing(
        provider_id=prof.id,
        title=payload.title,
        description=payload.description,
        ref_machine_id=payload.ref_machine_id,
        status=payload.status or "active",
    )
    db.add(l)
    db.commit()
    db.refresh(l)
    return shape_listing(l)


@router.get("/{listing_id}", response_model=dict)
def get_my_listing(
    listing_id: UUID,
    db: Session = Depends(get_db),
    current: User = Depends(require_provider),
) -> dict:
    prof = get_provider_profile(db, current.id)
    l = (
        db.query(Listing)
        .filter(Listing.id == listing_id, Listing.provider_id == prof.id)
        .first()
    )
    if not l:
        raise HTTPException(status_code=404, detail="Listing not found")
    return shape_listing(l)


@router.put("/{listing_id}", response_model=dict)
def update_listing(
    listing_id: UUID,
    payload: ListingUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(require_provider),
) -> dict:
    prof = get_provider_profile(db, current.id)
    l = (
        db.query(Listing)
        .filter(Listing.id == listing_id, Listing.provider_id == prof.id)
        .first()
    )
    if not l:
        raise HTTPException(status_code=404, detail="Listing not found")

    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(l, k, v)

    db.add(l)
    db.commit()
    db.refresh(l)
    return shape_listing(l)


@router.delete("/{listing_id}", status_code=204)
def delete_listing(
    listing_id: UUID,
    db: Session = Depends(get_db),
    current: User = Depends(require_provider),
):
    prof = get_provider_profile(db, current.id)
    l = (
        db.query(Listing)
        .filter(Listing.id == listing_id, Listing.provider_id == prof.id)
        .first()
    )
    if not l:
        raise HTTPException(status_code=404, detail="Listing not found")
    db.delete(l)
    db.commit()
