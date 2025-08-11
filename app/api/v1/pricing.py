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
from ...models.inventory import PricingRule  # SQLAlchemy model mapped to pricing_rules
from ...schemas.pricing import PricingCreate, PricingUpdate, PricingRead  # <-- important

router = APIRouter()


def get_provider_profile(db: Session, user_id: UUID) -> ProviderProfile:
    prof = db.query(ProviderProfile).filter(ProviderProfile.user_id == user_id).first()
    if not prof:
        raise HTTPException(status_code=403, detail="Provider profile required")
    return prof


@router.get("/", response_model=List[PricingRead])
def list_pricing_rules(
    db: Session = Depends(get_db),
    current: User = Depends(require_provider),
    owner_type: Optional[str] = Query(None, description="Filter: listing | machine"),
    owner_id: Optional[UUID] = Query(None, description="Filter by specific owner_id UUID"),
) -> List[PricingRead]:
    """
    List pricing rules belonging to the current provider.
    Optionally filter by owner_type and/or owner_id.
    """
    # NOTE: If your schema relates PricingRule -> Provider (via owner_id indirection),
    # you can add ownership checks here. For MVP, return by filters only.
    q = db.query(PricingRule)

    if owner_type:
        if owner_type not in ("listing", "machine"):
            raise HTTPException(status_code=400, detail="owner_type must be 'listing' or 'machine'")
        q = q.filter(PricingRule.owner_type == owner_type)
    if owner_id:
        q = q.filter(PricingRule.owner_id == owner_id)

    return q.order_by(PricingRule.unit.asc()).all()


@router.post("/", response_model=PricingRead, status_code=201)
def create_pricing_rule(
    payload: PricingCreate,
    db: Session = Depends(get_db),
    current: User = Depends(require_provider),
) -> PricingRead:
    if payload.owner_type not in ("listing", "machine"):
        raise HTTPException(status_code=400, detail="owner_type must be 'listing' or 'machine'")

    pr = PricingRule(
        owner_type=payload.owner_type,
        owner_id=payload.owner_id,
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
def update_pricing_rule(
    pricing_id: UUID,
    payload: PricingUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(require_provider),
) -> PricingRead:
    pr = db.query(PricingRule).filter(PricingRule.id == pricing_id).first()
    if not pr:
        raise HTTPException(status_code=404, detail="Pricing rule not found")

    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(pr, k, v)

    db.add(pr)
    db.commit()
    db.refresh(pr)
    return pr


@router.delete("/{pricing_id}", status_code=204)
def delete_pricing_rule(
    pricing_id: UUID,
    db: Session = Depends(get_db),
    current: User = Depends(require_provider),
):
    pr = db.query(PricingRule).filter(PricingRule.id == pricing_id).first()
    if not pr:
        raise HTTPException(status_code=404, detail="Pricing rule not found")
    db.delete(pr)
    db.commit()
