from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from ...database import get_db
from ...models.inventory import PricingRule, Machine
from ...models.profile import ProviderProfile
from ...schemas.pricing import PricingCreate, PricingUpdate, PricingRead
from ...dependencies.auth import require_provider
from ...models.user import User

router = APIRouter()

def get_provider_profile(db: Session, user_id: UUID) -> ProviderProfile:
    prof = db.query(ProviderProfile).filter(ProviderProfile.user_id == user_id).first()
    if not prof:
        raise HTTPException(status_code=403, detail="Provider profile required")
    return prof

def assert_ownership(db: Session, prof: ProviderProfile, owner_type: str, owner_id: UUID):
    if owner_type == "machine":
        m = db.query(Machine).filter(Machine.id == owner_id, Machine.provider_id == prof.id).first()
        if not m:
            raise HTTPException(status_code=403, detail="You do not own this machine")
    else:
        raise HTTPException(status_code=400, detail="Only machine pricing supported in v0.1")

@router.get("/", response_model=list[PricingRead])
def list_my_pricing(db: Session = Depends(get_db), current: User = Depends(require_provider)):
    prof = get_provider_profile(db, current.id)
    # only machine pricing in v0.1
    # fetch all rules where owner is one of my machines
    my_machine_ids = [row[0] for row in db.query(Machine.id).filter(Machine.provider_id == prof.id).all()]
    if not my_machine_ids:
        return []
    return db.query(PricingRule).filter(PricingRule.owner_type == "machine", PricingRule.owner_id.in_(my_machine_ids)).all()

@router.post("/", response_model=PricingRead, status_code=201)
def create_pricing(payload: PricingCreate, db: Session = Depends(get_db), current: User = Depends(require_provider)):
    prof = get_provider_profile(db, current.id)
    assert_ownership(db, prof, payload.owner_type, payload.owner_id)

    rule = PricingRule(**payload.model_dump(exclude_unset=True))
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule

@router.put("/{pricing_id}", response_model=PricingRead)
def update_pricing(pricing_id: UUID, payload: PricingUpdate, db: Session = Depends(get_db), current: User = Depends(require_provider)):
    prof = get_provider_profile(db, current.id)
    rule = db.query(PricingRule).filter(PricingRule.id == pricing_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Pricing rule not found")
    assert_ownership(db, prof, rule.owner_type, rule.owner_id)
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(rule, k, v)
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule

@router.delete("/{pricing_id}", status_code=204)
def delete_pricing(pricing_id: UUID, db: Session = Depends(get_db), current: User = Depends(require_provider)):
    prof = get_provider_profile(db, current.id)
    rule = db.query(PricingRule).filter(PricingRule.id == pricing_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Pricing rule not found")
    assert_ownership(db, prof, rule.owner_type, rule.owner_id)
    db.delete(rule)
    db.commit()
