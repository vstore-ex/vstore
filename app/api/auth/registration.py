from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.security import get_password_hash
from app.models.base import User, Role
from app.schemas import UserCreate, UserOut

router = APIRouter()

@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(
        (User.username == user_in.username) | (User.email == user_in.email)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="username or email already registered"
        )

    # get default role
    role = db.query(Role).filter(Role.name == "User").first()
    if not role:
        role = db.query(Role).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="no roles found in database"
            )

    new_user = User(
        username=user_in.username,
        email=user_in.email,
        password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        phone=user_in.phone,
        role_id=role.id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return UserOut(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        full_name=new_user.full_name,
        phone=new_user.phone,
        role_name=new_user.role.name
    )