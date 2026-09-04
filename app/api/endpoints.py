from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.models import User, Role
from app.schemas import UserOut
from app.api.auth.registration import router as registration_router
from app.api.auth.authentication import router as authentication_router
from app.api.auth.authorization import get_current_user

router = APIRouter()

# include auth routers
router.include_router(registration_router, prefix="/auth/register", tags=["auth"])
router.include_router(authentication_router, prefix="/auth", tags=["auth"])

@router.get("/")
async def root():
    return {"message": "welcome to vstore api. hello from pipeline"}