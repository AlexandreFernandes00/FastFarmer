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
from ...models.user import User
from ...models.profile import ProviderProfile
from ...models.inventory import Listing, PricingRule  # <-- PricingRule has listing_id FK

router = APIRouter()


# ----------------------- Pydantic payloads (CRUD) -----------------------
class ListingCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    ref_machine_id: Optional[UUID] = None
    status: Optional[str] = None  # e.g. active|paused|retired


class ListingUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    ref_machine_id: Optional[UUID] = None
    status: Optional[str] = None


# ---------------------------- Helpers -----------------------------------
def get_provider_profile(db: Session, user_id: UUID) -> ProviderProfile:
    prof = db.query(ProviderProfile).filter(ProviderProfile.user_id == user_id).first()
    if not prof:
        raise HTTPException(status_code=403, detail="Provider profile required")
    return prof


def shape_listing_base(l: Listing) -> Dict[str, Any]:
    return {
        "id": str(l.id),
        "title": l.title or "",
        "description": l.description or "",
        "status": (l.status or "active"),
        "ref_machine_id": str(l.ref_machine_id) if getattr(l, "ref_machine_id", None) else None,
        "created_at": getattr(l, "created_at", None),
        "updated_at": getattr(l, "updated_at", None),
    }


def shape_price(p: PricingRule) -> Dict[str, Any]:
    return {
        "id": str(p.id),
        "listing_id": str(p.listing_id),
        "unit": p.unit,                              # "hour" | "hectare" | "km" | "job"
        "base_price": float(p.base_price) if p.base_price is not None else None,
        "min_qty": p.min_qty,
        "transport_flat_fee": p.transport_flat_fee,
        "transport_per_km": p.transport_per_km,
        "currency": p.currency or "EUR",
        "surcharges": p.surcharges,
    }


def prices_summary_text(prices: List[Dict[str, Any]]) -> str:
    if not prices:
        return "Ask for a quote"
    # stable order by unit then price
    parts: List[str] = []
    for p in sorted(prices, key=lambda x: (x.get("unit") or "", x.get("base_price") or 0))[:3]:
        bp = p.get("base_price")
        cur = p.get("currency", "EUR")
        unit = p.get("unit") or ""
        seg = []
        if bp is not None and unit:
            text = f"{bp:g} {cur} / {unit}"
            if p.get("min_qty") not in (None, 0):
                text += f" (min {p['min_qty']})"
            seg.append(text)
        tf = p.get("transport_flat_fee")
        tkm = p.get("transport_per_km")
        if tf is not None or tkm is not None:
            tparts = []
            if tf is not None:
                tparts.append(f"flat {tf:g} {cur}")
            if tkm is not None:
                tparts.append(f"{tkm:g} {cur}/km")
            seg.append("transport: " + " + ".join(tparts))
        if seg:
            parts.append(" · ".join(seg))
    return " · ".join(parts) if parts else "Ask for a quote"


# --------------------------- PUBLIC (Marketplace) ------------------------
@router.get("/public")
def public_listings(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(None, description="Search in title/description"),
    include_pricing: bool = Query(True, description="Attach pricing rules"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> List[Dict[str, Any]]:
    # Show active or NULL status
    order_col = getattr(Listing, "created_at", Listing.id)
    stmt = sa.select(Listing).where(
        sa.or_(Listing.status == "active", Listing.status.is_(None))
    ).order_by(sa.desc(order_col)).limit(limit).offset(offset)

    if q:
        like = f"%{q.lower()}%"
        stmt = stmt.where(
            sa.or_(
                sa.func.lower(Listing.title).like(like),
                sa.func.lower(Listing.description).like(like),
            )
        )

    rows: List[Listing] = db.execute(stmt).scalars().all()
    shaped = [shape_listing_base(r) for r in rows]

    if not include_pricing or not rows:
        return shaped

    listing_ids = [r.id for r in rows]

    # Query listing-level pricing only (Option A)
    by_listing: Dict[UUID, List[Dict[str, Any]]] = {}
    if listing_ids:
        rules = (
            db.query(PricingRule)
            .filter(PricingRule.listing_id.in_(listing_ids))
            .all()
        )
        for p in rules:
            by_listing.setdefault(p.listing_id, []).append(shape_price(p))

    # Attach pricing
    for item in shaped:
        lid = UUID(item["id"])
        prices = by_listing.get(lid, [])
        item["pricing"] = prices
        item["prices_text"] = prices_summary_text(prices)

    return shaped


@router.get("/public/{listing_id}")
def public_get_one(
    listing_id: UUID,
    db: Session = Depends(get_db),
    include_pricing: bool = Query(True),
) -> Dict[str, Any]:
    l = db.get(Listing, listing_id)
    if not l or (l.status not in (None, "active")):
        raise HTTPException(status_code=404, detail="Listing not found")
    shaped = shape_listing_base(l)

    if include_pricing:
        prices = [
            shape_price(p) for p in db.query(PricingRule)
            .filter(PricingRule.listing_id == listing_id)
            .all()
        ]
        shaped["pricing"] = prices
        shaped["prices_text"] = prices_summary_text(prices)

    return shaped


# --------------------------- PROVIDER CRUD -------------------------------
@router.get("/", response_model=List[Dict[str, Any]])
def my_listings(
    db: Session = Depends(get_db),
    current: User = Depends(require_provider),
) -> List[Dict[str, Any]]:
    prof = get_provider_profile(db, current.id)
    order_col = getattr(Listing, "created_at", Listing.id)
    rows = (
        db.query(Listing)
        .filter(Listing.provider_id == prof.id)
        .order_by(sa.desc(order_col))
        .all()
    )
    return [shape_listing_base(r) for r in rows]


@router.post("/", response_model=Dict[str, Any], status_code=201)
def create_listing(
    payload: ListingCreate,
    db: Session = Depends(get_db),
    current: User = Depends(require_provider),
) -> Dict[str, Any]:
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


@router.get("/{listing_id}", response_model=Dict[str, Any])
def get_my_listing(
    listing_id: UUID,
    db: Session = Depends(get_db),
    current: User = Depends(require_provider),
) -> Dict[str, Any]:
    prof = get_provider_profile(db, current.id)
    l = (
        db.query(Listing)
        .filter(Listing.id == listing_id, Listing.provider_id == prof.id)
        .first()
    )
    if not l:
        raise HTTPException(status_code=404, detail="Listing not found")
    return shape_listing_base(l)


@router.put("/{listing_id}", response_model=Dict[str, Any])
def update_listing(
    listing_id: UUID,
    payload: ListingUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(require_provider),
) -> Dict[str, Any]:
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
