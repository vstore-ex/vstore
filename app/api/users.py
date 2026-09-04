from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.user import User, Role
from app.schemas import UserOut, UserUpdate
from app.api.auth.authorization import get_current_user, require_admin

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=List[UserOut])
async def list_public_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    result = []
    for u in users:
        data = u.__dict__.copy()
        data["role_name"] = u.role.name
        result.append(UserOut(**data))
    return result

@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    data = current_user.__dict__.copy()
    data["role_name"] = current_user.role.name
    return UserOut(**data)

@router.get("/{user_id}", response_model=UserOut)
async def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="user not found")

    data = user.__dict__.copy()
    data["role_name"] = user.role.name
    return UserOut(**data)

@router.put("/me", response_model=UserOut)
async def update_me(
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    update_data = user_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)

    data = current_user.__dict__.copy()
    data["role_name"] = current_user.role.name
    return UserOut(**data)


# admin

@router.get("/admin", response_model=List[UserOut])
async def list_all_users(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    users = db.query(User).offset(skip).limit(limit).all()

    result = []
    for u in users:
        data = u.__dict__.copy()
        data["role_name"] = u.role.name
        result.append(UserOut(**data))
    return result

@router.put("/admin/{user_id}", response_model=UserOut)
async def update_user_admin(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="user not found")

    update_data = user_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)

    data = user.__dict__.copy()
    data["role_name"] = user.role.name
    return UserOut(**data)

@router.post("/admin/{user_id}/toggle-ban")
async def toggle_user_ban(
    user_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="user not found")

    user.is_banned = not user.is_banned
    db.commit()
    db.refresh(user)

    status_text = "banned" if user.is_banned else "unbanned"
    return {
        "message": f"user {user.username} has been {status_text}",
        "is_banned": user.is_banned
    }

@router.delete("/admin/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_admin(
    user_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="user not found")
    db.delete(user)
    db.commit()
    return None