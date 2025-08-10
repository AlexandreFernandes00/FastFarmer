from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User
from ..utils.security import decode_token
from ..config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/token")

class AuthError(HTTPException):
    def __init__(self, code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials"):
        super().__init__(status_code=code, detail=detail, headers={"WWW-Authenticate": "Bearer"})

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        payload = decode_token(token)
        sub = payload.get("sub")
        if not sub:
            raise AuthError()
        user_id = UUID(str(sub))
    except Exception:
        raise AuthError()

    user = db.query(User).get(user_id)
    if not user:
        raise AuthError()
    return user

def require_client(current: User = Depends(get_current_user)) -> User:
    if not current.is_client:
        raise HTTPException(status_code=403, detail="Client role required")
    return current

def require_provider(current: User = Depends(get_current_user)) -> User:
    if not current.is_provider:
        raise HTTPException(status_code=403, detail="Provider role required")
    return current

def require_admin(current: User = Depends(get_current_user)) -> User:
    if not current.is_admin:
        raise HTTPException(status_code=403, detail="Admin role required")
    return current
