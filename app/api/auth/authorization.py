from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.security import decode_access_token
from app.models.base import User
from typing import Optional

async def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # get token from cookies instead of authorization header
    token = request.cookies.get("access_token")
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
            detail="this account has been banned"
        )

    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    return current_user
