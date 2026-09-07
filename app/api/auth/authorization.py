from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Optional

from app.core.db import get_db
from app.core.security import decode_access_token
from app.models import User

async def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = request.headers.get("Authorization")
    if token and token.startswith("Bearer "):
        token = token.split(" ")[1]
    elif not (token := request.cookies.get("access_token")):
        token = None

    if not token:
        raise credentials_exception

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    username: str = payload.get("sub")
    if not username:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception

    if user.is_banned:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="account banned"
        )

    return user

async def get_optional_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[User]:
    token = request.headers.get("Authorization")
    if token and token.startswith("Bearer "):
        token = token.split(" ")[1]
    elif not (token := request.cookies.get("access_token")):
        token = None

    if not token:
        return None

    payload = decode_access_token(token)
    if payload is None:
        return None

    username: str = payload.get("sub")
    if not username:
        return None

    user = db.query(User).filter(User.username == username).first()
    if user is None or user.is_banned:
        return None

    return user

async def get_current_active_user(

    current_user: User = Depends(get_current_user)
) -> User:
    return current_user

async def require_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    is_admin = (
        current_user.role.name.lower() in ["admin"] or
        getattr(current_user.role, "can_ban", False)
    )
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="admin required"
        )

    return current_user