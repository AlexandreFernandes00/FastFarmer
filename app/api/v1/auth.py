from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...database import get_db
from ...models.user import User
from ...schemas.user import UserRegister, UserRead
from ...utils.security import get_password_hash

router = APIRouter()

@router.post("/register", response_model=UserRead, status_code=201)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    # no admin from this endpoint — ever
    email = payload.email.strip().lower()
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already exists")

    if payload.customer_type == "client":
        is_client, is_provider = True, False
    elif payload.customer_type == "provider":
        is_client, is_provider = False, True
    else:  # both
        is_client, is_provider = True, True

    user = User(
        email=email,
        full_name=payload.full_name.strip(),
        phone=payload.phone,
        password_hash=get_password_hash(payload.password),
        is_client=is_client,
        is_provider=is_provider,
        is_admin=False,  # force block admin
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
