# app/api/v1/requests.py
from __future__ import annotations

from typing import List
from uuid import UUID


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...database import get_db
from ...dependencies.auth import require_client, require_provider
from ...models.user import User
from ...models.profile import ClientProfile, ProviderProfile
from ...models.geo import Field                       # adjust path if different
from ...models.inventory import Listing               # used to validate listing_id
from ...models.workflow import WorkRequest, RequestStatus
from ...schemas.request import WorkRequestCreate, WorkRequestUpdate, WorkRequestRead

router = APIRouter()


# ------------------------- Helpers -------------------------
def get_client_profile(db: Session, user_id: UUID) -> ClientProfile:
    prof = db.query(ClientProfile).filter(ClientProfile.user_id == user_id).first()
    if not prof:
        raise HTTPException(status_code=403, detail="Client profile required")
    return prof

def get_provider_profile(db: Session, user_id: UUID) -> ProviderProfile:
    prof = db.query(ProviderProfile).filter(ProviderProfile.user_id == user_id).first()
    if not prof:
        raise HTTPException(status_code=403, detail="Provider profile required")
    return prof


# ---------------------- Client endpoints -------------------
@router.get("/me", response_model=List[WorkRequestRead])
def list_my_requests(
    db: Session = Depends(get_db),
    current: User = Depends(require_client),
):
    cprof = get_client_profile(db, current.id)
    return (
        db.query(WorkRequest)
        .filter(WorkRequest.client_id == cprof.id)
        .order_by(WorkRequest.created_at.desc())
        .all()
    )


@router.post("/", response_model=WorkRequestRead, status_code=201)
def create_request(
    payload: WorkRequestCreate,
    db: Session = Depends(get_db),
    current: User = Depends(require_client),
):
    cprof = get_client_profile(db, current.id)

    # 1) Field must belong to this client
    field = (
        db.query(Field)
        .filter(Field.id == payload.field_id, Field.client_id == cprof.id)
        .first()
    )
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")

    # 2) Listing must exist and be active (or NULL treated as active)
    listing = db.get(Listing, payload.listing_id)
    if not listing or getattr(listing, "status", "active") not in (None, "active"):
        raise HTTPException(status_code=404, detail="Listing not found or not active")

    # 3) Create WorkRequest; set status explicitly to 'open'
    req = WorkRequest(
        client_id=cprof.id,
        listing_id=payload.listing_id,
        field_id=payload.field_id,
        desired_date=payload.desired_date,
        time_window=payload.time_window,
        notes=payload.notes,
        status=RequestStatus.open,  # enum-safe
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    return req


@router.put("/{request_id}", response_model=WorkRequestRead)
def update_my_request(
    request_id: UUID,
    payload: WorkRequestUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(require_client),
):
    cprof = get_client_profile(db, current.id)
    req = (
        db.query(WorkRequest)
        .filter(WorkRequest.id == request_id, WorkRequest.client_id == cprof.id)
        .first()
    )
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    # Only allow client-editable fields (not status progression here)
    data = payload.model_dump(exclude_unset=True)
    for k in ("desired_date", "time_window", "notes"):
        if k in data:
            setattr(req, k, data[k])

    db.add(req)
    db.commit()
    db.refresh(req)
    return req


# --------------------- Provider endpoints ------------------
@router.get("/open", response_model=List[WorkRequestRead])
def list_open_requests_for_providers(
    db: Session = Depends(get_db),
    current: User = Depends(require_provider),
):
    # Enum-safe filter: translates to request_status enum in PG
    rows = (
        db.query(WorkRequest)
        .filter(WorkRequest.status.in_([RequestStatus.open, RequestStatus.quoted]))
        .order_by(WorkRequest.created_at.desc())
        .all()
    )
    return rows
