from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from ...database import get_db
from ...dependencies.auth import require_provider, require_client
from ...models.user import User
from ...models.profile import ProviderProfile, ClientProfile
from ...models.workflow import Quote, WorkRequest
from ...schemas.quote import QuoteCreate, QuoteUpdate, QuoteRead

router = APIRouter()

def get_provider_profile(db: Session, user_id: UUID) -> ProviderProfile:
    prof = db.query(ProviderProfile).filter(ProviderProfile.user_id == user_id).first()
    if not prof: raise HTTPException(status_code=403, detail="Provider profile required")
    return prof

def get_client_profile(db: Session, user_id: UUID) -> ClientProfile:
    prof = db.query(ClientProfile).filter(ClientProfile.user_id == user_id).first()
    if not prof: raise HTTPException(status_code=403, detail="Client profile required")
    return prof

# Provider creates a quote
@router.post("/", response_model=QuoteRead, status_code=201)
def create_quote(payload: QuoteCreate, db: Session = Depends(get_db), current: User = Depends(require_provider)):
    prof = get_provider_profile(db, current.id)
    req = db.query(WorkRequest).filter(WorkRequest.id == payload.request_id).first()
    if not req or req.status not in ("open", "quoted"):
        raise HTTPException(status_code=400, detail="Request not open")
    q = Quote(provider_id=prof.id, **payload.model_dump())
    db.add(q)
    # mark request as quoted (still visible)
    req.status = "quoted"
    db.add(req)
    db.commit()
    db.refresh(q)
    return q

# Provider updates/withdraws a quote
@router.put("/{quote_id}", response_model=QuoteRead)
def update_quote(quote_id: UUID, payload: QuoteUpdate, db: Session = Depends(get_db), current: User = Depends(require_provider)):
    prof = get_provider_profile(db, current.id)
    q = db.query(Quote).filter(Quote.id == quote_id, Quote.provider_id == prof.id).first()
    if not q: raise HTTPException(status_code=404, detail="Quote not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(q, k, v)
    db.add(q); db.commit(); db.refresh(q)
    return q

# Client: list quotes for my request
@router.get("/for-request/{request_id}", response_model=list[QuoteRead])
def quotes_for_request(request_id: UUID, db: Session = Depends(get_db), current: User = Depends(require_client)):
    cprof = get_client_profile(db, current.id)
    req = db.query(WorkRequest).filter(WorkRequest.id == request_id).first()
    if not req: raise HTTPException(status_code=404, detail="Request not found")
    # ensure ownership
    if req.client_id != cprof.id: raise HTTPException(status_code=403, detail="Forbidden")
    return db.query(Quote).filter(Quote.request_id == request_id).order_by(Quote.created_at.desc()).all()
