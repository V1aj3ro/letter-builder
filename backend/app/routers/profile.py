from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..models import User
from ..schemas import UserOut, ProfileUpdate, PasswordChange
from ..auth import verify_password, hash_password
from ..dependencies import get_approved_user

router = APIRouter()


@router.get("", response_model=UserOut)
async def get_profile(current_user: User = Depends(get_approved_user)):
    return current_user


@router.patch("", response_model=UserOut)
async def update_profile(
    data: ProfileUpdate,
    current_user: User = Depends(get_approved_user),
    db: AsyncSession = Depends(get_db),
):
    if data.full_name is not None:
        current_user.full_name = data.full_name
    if data.position is not None:
        current_user.position = data.position
    if data.phone is not None:
        current_user.phone = data.phone
    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.patch("/password")
async def change_password(
    data: PasswordChange,
    current_user: User = Depends(get_approved_user),
    db: AsyncSession = Depends(get_db),
):
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    current_user.hashed_password = hash_password(data.new_password)
    await db.commit()
    return {"message": "Password updated"}
