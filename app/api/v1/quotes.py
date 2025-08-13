# app/api/v1/quotes.py
import decimal
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ...database import get_db
from ...dependencies.auth import require_user, require_provider
from ...models.user import User
from ...models.workflow import WorkRequest, Quote, QuoteItem, QuoteStatus, RequestStatus
from ...models.profile import ProviderProfile
from ...models.inventory import Listing
from ...schemas.quotes import QuoteCreate, QuoteRead

router = APIRouter()

def get_provider_profile(db: Session, user_id: UUID) -> ProviderProfile:
    prof = db.query(ProviderProfile).filter(ProviderProfile.user_id == user_id).first()
    if not prof:
        raise HTTPException(status_code=403, detail="Provider profile required")
    return prof

def d(v) -> decimal.Decimal:
    if v is None: return decimal.Decimal("0")
    if isinstance(v, decimal.Decimal): return v
    return decimal.Decimal(str(v))

@router.post("/", response_model=QuoteRead, status_code=201)
def create_quote(
    payload: QuoteCreate,
    db: Session = Depends(get_db),
    current: User = Depends(require_provider),
):
    prof = get_provider_profile(db, current.id)

    req = db.query(WorkRequest).filter(WorkRequest.id == payload.request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    # Provider must own the listing on the request
    lst = db.query(Listing).filter(Listing.id == req.listing_id).first()
    if not lst or lst.provider_id != prof.id:
        raise HTTPException(status_code=403, detail="You don't own this listing/request")

    if req.status not in (RequestStatus.open, RequestStatus.quoted):
        raise HTTPException(status_code=400, detail=f"Cannot quote a request with status {req.status}")

    # Build items + totals
    items = []
    subtotal = decimal.Decimal("0")
    for it in payload.items:
        lt = d(it.line_total)
        subtotal += lt
        items.append(QuoteItem(
            kind=it.kind,
            description=it.description,
            unit=it.unit,
            qty=d(it.qty) if it.qty is not None else None,
            unit_price=d(it.unit_price) if it.unit_price is not None else None,
            line_total=lt,
        ))

    transport_fee = d(payload.transport_fee)
    total = subtotal + transport_fee

    q = Quote(
        request_id=req.id,
        provider_id=prof.id,
        currency=payload.currency.upper(),
        message=payload.message,
        subtotal=subtotal,
        transport_fee=transport_fee if payload.transport_fee is not None else None,
        surcharges=payload.surcharges,
        total=total,
        status=QuoteStatus.offered,
        expires_at=payload.expires_at,
    )
    q.items = items
    db.add(q)

    # Move request to 'quoted' if it was 'open'
    if req.status == RequestStatus.open:
        req.status = RequestStatus.quoted
        db.add(req)

    db.commit()
    db.refresh(q)
    return q

@router.get("/for-request/{request_id}", response_model=list[QuoteRead])
def quotes_for_request(
    request_id: UUID,
    db: Session = Depends(get_db),
    current: User = Depends(require_user),
):
    # Either the client who created it or the provider who owns listing can see quotes
    req = db.query(WorkRequest).filter(WorkRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    # If you keep client_profile_id on WorkRequest, adapt this check
    if current.id != req.client_id:
        # check provider ownership
        lst = db.query(Listing).filter(Listing.id == req.listing_id).first()
        prof = db.query(ProviderProfile).filter(ProviderProfile.user_id == current.id).first()
        if not (lst and prof and lst.provider_id == prof.id):
            raise HTTPException(status_code=403, detail="Not allowed")

    rows = db.query(Quote).filter(Quote.request_id == request_id).order_by(Quote.created_at.desc()).all()
    return rows

@router.post("/{quote_id}/withdraw", status_code=204)
def withdraw_quote(
    quote_id: UUID,
    db: Session = Depends(get_db),
    current: User = Depends(require_provider),
):
    prof = get_provider_profile(db, current.id)
    q = db.query(Quote).filter(Quote.id == quote_id, Quote.provider_id == prof.id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Quote not found")
    if q.status != QuoteStatus.offered:
        raise HTTPException(status_code=400, detail="Only offered quotes can be withdrawn")
    q.status = QuoteStatus.withdrawn
    db.add(q)
    db.commit()
    return

@router.post("/{quote_id}/accept", status_code=200, response_model=QuoteRead)
def accept_quote(
    quote_id: UUID,
    db: Session = Depends(get_db),
    current: User = Depends(require_user),
):
    q = db.query(Quote).filter(Quote.id == quote_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Quote not found")

    req = db.query(WorkRequest).filter(WorkRequest.id == q.request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Related request not found")
    # Client who owns the request only
    if req.client_id != current.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    if q.status != QuoteStatus.offered:
        raise HTTPException(status_code=400, detail="Cannot accept this quote")

    # Accept this one, reject others (unique partial index enforces single accepted)
    q.status = QuoteStatus.accepted
    db.add(q)
    db.query(Quote).filter(Quote.request_id == req.id, Quote.id != q.id, Quote.status == QuoteStatus.offered)\
        .update({Quote.status: QuoteStatus.rejected}, synchronize_session=False)

    # Move request forward
    req.status = RequestStatus.accepted
    db.add(req)

    db.commit()
    db.refresh(q)
    return q
