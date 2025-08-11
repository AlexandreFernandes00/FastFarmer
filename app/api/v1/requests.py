from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from ...database import get_db
from ...dependencies.auth import require_client, require_provider
from ...models.user import User
from ...models.profile import ClientProfile, ProviderProfile
from ...models.geo import Field
from ...models.workflow import WorkRequest
from ...schemas.request import WorkRequestCreate, WorkRequestUpdate, WorkRequestRead

router = APIRouter()

def get_client_profile(db: Session, user_id: UUID) -> ClientProfile:
    prof = db.query(ClientProfile).filter(ClientProfile.user_id == user_id).first()
    if not prof: raise HTTPException(status_code=403, detail="Client profile required")
    return prof

def get_provider_profile(db: Session, user_id: UUID) -> ProviderProfile:
    prof = db.query(ProviderProfile).filter(ProviderProfile.user_id == user_id).first()
    if not prof: raise HTTPException(status_code=403, detail="Provider profile required")
    return prof

# Client: my requests
@router.get("/me", response_model=list[WorkRequestRead])
def list_my_requests(db: Session = Depends(get_db), current: User = Depends(require_client)):
    prof = get_client_profile(db, current.id)
    return db.query(WorkRequest).filter(WorkRequest.client_id == prof.id).order_by(WorkRequest.created_at.desc()).all()

@router.post("/", response_model=WorkRequestRead, status_code=201)
def create_request(payload: WorkRequestCreate, db: Session = Depends(get_db), current: User = Depends(require_client)):
    prof = get_client_profile(db, current.id)
    # ensure field belongs to this client
    field = db.query(Field).filter(Field.id == payload.field_id, Field.client_id == prof.id).first()
    if not field: raise HTTPException(status_code=404, detail="Field not found")
    req = WorkRequest(client_id=prof.id, **payload.model_dump())
    db.add(req); db.commit(); db.refresh(req)
    return req

@router.put("/{request_id}", response_model=WorkRequestRead)
def update_request(request_id: UUID, payload: WorkRequestUpdate, db: Session = Depends(get_db), current: User = Depends(require_client)):
    prof = get_client_profile(db, current.id)
    req = db.query(WorkRequest).filter(WorkRequest.id == request_id, WorkRequest.client_id == prof.id).first()
    if not req: raise HTTPException(status_code=404, detail="Request not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(req, k, v)
    db.add(req); db.commit(); db.refresh(req)
    return req

# Provider: browse open requests (MVP — no geo filter yet)
@router.get("/open", response_model=list[WorkRequestRead])
def open_requests(db: Session = Depends(get_db), current: User = Depends(require_provider)):
    # later: filter by distance, category, etc.
    return db.query(WorkRequest).filter(WorkRequest.status.in_(["open","quoted"])).order_by(WorkRequest.created_at.desc()).all()
