from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.models.base import User, Role
from app.schemas import UserOut
from app.api.auth.registration import router as registration_router
from app.api.auth.authentication import router as authentication_router
from app.api.auth.authorization import get_current_user

router = APIRouter()

# Include auth routers
router.include_router(registration_router, prefix="/auth/register", tags=["auth"])
router.include_router(authentication_router, prefix="/auth", tags=["auth"])

@router.get("/")
async def root():
    return {"message": "welcome to vstore api. hello from pipeline"}

@router.get("/users/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role.name
    }

# for simple front
@router.get("/users/public")
async def get_public_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [
        {
            "id": u.id,
            "username": u.username,
            "role_name": u.role.name
        }
        for u in users
    ]


# for admin-panel
@router.get("/admin/users")
async def get_admin_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "full_name": u.full_name,
            "phone": u.phone,
            "role_name": u.role.name,
            "is_banned": u.is_banned
        }
        for u in users
    ]

@router.post("/admin/users/{user_id}/toggle-ban")
async def toggle_user_ban(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user not found"
        )

    user.is_banned = not user.is_banned
    db.commit()
    db.refresh(user)

    status_text = "banned" if user.is_banned else "unbanned"
    return {
        "message": f"user {user.username} has been {status_text}",
        "is_banned": user.is_banned
    }
