from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ...database import get_db
from ...models.user import User
from ...schemas.user import UserCreate, UserRead
from ...utils.security import get_password_hash, verify_password, create_access_token
from ...dependencies.auth import get_current_user

router = APIRouter()

@router.post("/register", response_model=UserRead, status_code=201)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already exists")

    if payload.customer_type == "client":
        is_client, is_provider = True, False
    elif payload.customer_type == "provider":
        is_client, is_provider = False, True
    else:
        is_client, is_provider = True, True

    user = User(
        email=email,
        full_name=payload.full_name.strip(),
        phone=payload.phone,
        password_hash=get_password_hash(payload.password),
        is_client=is_client,
        is_provider=is_provider,
        is_admin=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# OAuth2 password flow (form-encoded): username=email, password=pass
@router.post("/token")
def token(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # username is email in our case
    email = form.username.strip().lower()
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token(subject=user.id, extra={"email": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# JSON login (if you want to call from your own form instead of OAuth2)
@router.post("/login")
def login(payload: dict, db: Session = Depends(get_db)):
    email = str(payload.get("email", "")).strip().lower()
    password = str(payload.get("password", ""))
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token = create_access_token(subject=user.id, extra={"email": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserRead)
def me(current: User = Depends(get_current_user)):
    return current
