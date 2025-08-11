# app/api/v1/listings.py
from __future__ import annotations

from typing import List, Optional, Dict, Any
from uuid import UUID

import sqlalchemy as sa
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ...database import get_db
from ...dependencies.auth import require_provider
from ...models.inventory import Listing  # adjust path if needed
from ...models.profile import ProviderProfile
from ...models.user import User
from ...models.pricing_rule import PricingRule 

router = APIRouter()


# --------- Pydantic payloads for provider CRUD ---------
class ListingCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    ref_machine_id: Optional[UUID] = None
    status: Optional[str] = None


class ListingUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    ref_machine_id: Optional[UUID] = None
    status: Optional[str] = None


# --------- Helpers ---------
def get_provider_profile(db: Session, user_id: UUID) -> ProviderProfile:
    prof = db.query(ProviderProfile).filter(ProviderProfile.user_id == user_id).first()
    if not prof:
        raise HTTPException(status_code=403, detail="Provider profile required")
    return prof


def shape_listing_base(l: Listing) -> dict:
    return {
        "id": str(l.id),
        "title": l.title or "",
        "description": l.description or "",
        "status": (l.status or "active"),
        "ref_machine_id": str(getattr(l, "ref_machine_id", "")) if getattr(l, "ref_machine_id", None) else None,
        "created_at": getattr(l, "created_at", None),
        "updated_at": getattr(l, "updated_at", None),
    }


def shape_price(p: PricingRule) -> dict:
    return {
        "id": str(p.id),
        "owner_type": p.owner_type,
        "owner_id": str(p.owner_id),
        "unit": p.unit,
        "base_price": float(p.base_price) if p.base_price is not None else None,
        "min_qty": p.min_qty,
        "transport_flat_fee": p.transport_flat_fee,
        "transport_per_km": p.transport_per_km,
        "currency": p.currency or "EUR",
        "surcharges": p.surcharges,
    }


def prices_summary_text(prices: List[dict]) -> str:
    # build a short, readable summary for the card
    # prefer listing-level prices (owner_type == "listing"); fall back to machine-level
    if not prices:
        return "Ask for a quote"
    # keep the order stable: listing-level first, then machine-level, then by unit
    def sort_key(x):
        return (0 if x.get("owner_type") == "listing" else 1, x.get("unit") or "", x.get("base_price") or 0)
    items = sorted(prices, key=sort_key)
    parts = []
    for p in items[:3]:
        bp = p.get("base_price")
        cur = p.get("currency", "EUR")
        unit = p.get("unit") or ""
        if bp is not None and unit:
            parts.append(f"{bp:g} {cur} / {unit}")
    return " · ".join(parts) if parts else "Ask for a quote"


# --------- PUBLIC READ (Marketplace) ---------
@router.get("/public")
def public_listings(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(None, description="Search in title/description"),
    include_pricing: bool = Query(True, description="Attach pricing rules"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> List[dict]:
    # base query: show active (or NULL) status
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

    rows: list[Listing] = db.execute(stmt).scalars().all()
    shaped = [shape_listing_base(r) for r in rows]

    if not include_pricing or not rows:
        return shaped

    # Collect IDs for pricing lookup
    listing_ids = [r.id for r in rows]
    machine_ids = [r.ref_machine_id for r in rows if getattr(r, "ref_machine_id", None)]

    # Fetch listing-level pricing
    lp = []
    if listing_ids:
        lp = (
            db.query(PricingRule)
            .filter(PricingRule.owner_type == "listing",
                    PricingRule.owner_id.in_(listing_ids))
            .all()
        )

    # Fetch machine-level pricing (fallback)
    mp = []
    if machine_ids:
        mp = (
            db.query(PricingRule)
            .filter(PricingRule.owner_type == "machine",
                    PricingRule.owner_id.in_(machine_ids))
            .all()
        )

    # Index by owner_id
    by_listing: Dict[UUID, List[dict]] = {}
    for p in lp:
        by_listing.setdefault(p.owner_id, []).append(shape_price(p))

    by_machine: Dict[UUID, List[dict]] = {}
    for p in mp:
        by_machine.setdefault(p.owner_id, []).append(shape_price(p))

    # Attach pricing to each listing (listing-level first, then machine-level)
    for item in shaped:
        prices: List[dict] = []
        lid = UUID(item["id"])
        rid = item.get("ref_machine_id")
        if lid in by_listing:
            prices.extend(by_listing[lid])
        if rid:
            try:
                rid_uuid = UUID(rid)
                if rid_uuid in by_machine:
                    prices.extend(by_machine[rid_uuid])
            except Exception:
                pass
        item["pricing"] = prices
        item["prices_text"] = prices_summary_text(prices)

    return shaped


@router.get("/public/{listing_id}")
def public_get_one(
    listing_id: UUID,
    db: Session = Depends(get_db),
    include_pricing: bool = Query(True),
) -> dict:
    l = db.get(Listing, listing_id)
    if not l or (l.status not in (None, "active")):
        raise HTTPException(status_code=404, detail="Listing not found")
    shaped = shape_listing_base(l)
    if include_pricing:
        prices: List[dict] = []
        # listing-level
        lp = (
            db.query(PricingRule)
            .filter(PricingRule.owner_type == "listing",
                    PricingRule.owner_id == listing_id)
            .all()
        )
        if getattr(l, "ref_machine_id", None):
            mp = (
                db.query(PricingRule)
                .filter(PricingRule.owner_type == "machine",
                        PricingRule.owner_id == l.ref_machine_id)
                .all()
            )
        prices.extend([shape_price(p) for p in lp])
        # machine-level
        if getattr(l, "ref_machine_id", None):
            mp = (
                db.query(Pricing)
                .filter(Pricing.owner_type == "machine", Pricing.owner_id == l.ref_machine_id)
                .all()
            )
            prices.extend([shape_price(p) for p in mp])
        shaped["pricing"] = prices
        shaped["prices_text"] = prices_summary_text(prices)
    return shaped


# --------- PROVIDER CRUD (unchanged) ---------
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
    return [shape_listing_base(r) for r in rows]


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
    return shape_listing_base(l)


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
    return shape_listing_base(l)


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
    return shape_listing_base(l)


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
