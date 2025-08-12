# app/api/v1/pricing.py
from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ...database import get_db
from ...dependencies.auth import require_provider
from ...models.user import User
from ...models.profile import ProviderProfile
from ...models.inventory import PricingRule, Listing
from ...schemas.pricing import (
    PricingCreate, PricingPut, PricingUpdate, PricingRead
)

router = APIRouter()

def get_provider_profile(db: Session, user_id: UUID) -> ProviderProfile:
    prof = db.query(ProviderProfile).filter(ProviderProfile.user_id == user_id).first()
    if not prof:
        raise HTTPException(status_code=403, detail="Provider profile required")
    return prof

def assert_listing_ownership(db: Session, provider_id: UUID, listing_id: UUID):
    # listing must exist and belong to current provider
    lst = db.query(Listing).filter(Listing.id == listing_id, Listing.provider_id == provider_id).first()
    if not lst:
        raise HTTPException(status_code=404, detail="Listing not found or not yours")

@router.get("/", response_model=List[PricingRead])
def list_pricing_rules(
    db: Session = Depends(get_db),
    current: User = Depends(require_provider),
    listing_id: Optional[UUID] = Query(None, description="Filter by listing"),
) -> List[PricingRead]:
    prof = get_provider_profile(db, current.id)
    q = db.query(PricingRule).join(Listing, PricingRule.listing_id == Listing.id).filter(Listing.provider_id == prof.id)
    if listing_id:
        q = q.filter(PricingRule.listing_id == listing_id)
    return q.order_by(PricingRule.unit.asc()).all()

@router.post("/", response_model=PricingRead, status_code=201)
def create_pricing_rule(
    payload: PricingCreate,
    db: Session = Depends(get_db),
    current: User = Depends(require_provider),
) -> PricingRead:
    prof = get_provider_profile(db, current.id)
    # validation: listing exists and is owned by provider
    assert_listing_ownership(db, prof.id, payload.listing_id)

    pr = PricingRule(
        listing_id=payload.listing_id,
        unit=payload.unit,
        base_price=payload.base_price,
        min_qty=payload.min_qty,
        transport_flat_fee=payload.transport_flat_fee,
        transport_per_km=payload.transport_per_km,
        currency=payload.currency or "EUR",
        surcharges=payload.surcharges,
    )
    db.add(pr)
    db.commit()
    db.refresh(pr)
    return pr

@router.put("/{pricing_id}", response_model=PricingRead)
def put_pricing_rule(
    pricing_id: UUID,
    payload: PricingPut,
    db: Session = Depends(get_db),
    current: User = Depends(require_provider),
) -> PricingRead:
    prof = get_provider_profile(db, current.id)
    pr = db.query(PricingRule).filter(PricingRule.id == pricing_id).first()
    if not pr:
        raise HTTPException(status_code=404, detail="Pricing rule not found")

    # ensure old listing belongs to provider (and if changing listing_id, ensure new one too)
    assert_listing_ownership(db, prof.id, pr.listing_id)
    if payload.listing_id != pr.listing_id:
        assert_listing_ownership(db, prof.id, payload.listing_id)

    pr.listing_id = payload.listing_id
    pr.unit = payload.unit
    pr.base_price = payload.base_price
    pr.min_qty = payload.min_qty
    pr.transport_flat_fee = payload.transport_flat_fee
    pr.transport_per_km = payload.transport_per_km
    pr.currency = payload.currency or "EUR"
    pr.surcharges = payload.surcharges

    db.add(pr); db.commit(); db.refresh(pr)
    return pr

@router.patch("/{pricing_id}", response_model=PricingRead)
def patch_pricing_rule(
    pricing_id: UUID,
    payload: PricingUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(require_provider),
) -> PricingRead:
    prof = get_provider_profile(db, current.id)
    pr = db.query(PricingRule).filter(PricingRule.id == pricing_id).first()
    if not pr:
        raise HTTPException(status_code=404, detail="Pricing rule not found")

    # ownership of current listing
    assert_listing_ownership(db, prof.id, pr.listing_id)

    data = payload.model_dump(exclude_unset=True)

    # if moving to another listing, validate the new one belongs to provider
    if "listing_id" in data and data["listing_id"] != pr.listing_id:
        assert_listing_ownership(db, prof.id, data["listing_id"])
        pr.listing_id = data["listing_id"]

    for k in ("unit", "base_price", "min_qty", "transport_flat_fee", "transport_per_km", "currency", "surcharges"):
        if k in data:
            setattr(pr, k, data[k] if k != "currency" else (data[k] or "EUR"))

    db.add(pr); db.commit(); db.refresh(pr)
    return pr

@router.delete("/{pricing_id}", status_code=204)
def delete_pricing_rule(
    pricing_id: UUID,
    db: Session = Depends(get_db),
    current: User = Depends(require_provider),
):
    prof = get_provider_profile(db, current.id)
    pr = db.query(PricingRule).filter(PricingRule.id == pricing_id).first()
    if not pr:
        raise HTTPException(status_code=404, detail="Pricing rule not found")
    # ensure ownership
    assert_listing_ownership(db, prof.id, pr.listing_id)
    db.delete(pr); db.commit()
