from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from ..database import get_db
from ..models import User
from ..schemas import RegisterRequest, LoginRequest, TokenResponse, PendingResponse
from ..auth import hash_password, verify_password, create_access_token

router = APIRouter()


@router.post("/register")
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # Check email uniqueness
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Check if this is the first user
    count_result = await db.execute(select(func.count()).select_from(User))
    user_count = count_result.scalar()

    is_first = user_count == 0

    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
        is_admin=is_first,
        is_approved=is_first,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    if is_first:
        token = create_access_token({"sub": str(user.id)})
        return TokenResponse(access_token=token)

    return PendingResponse(message="pending_approval")


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_approved:
        raise HTTPException(status_code=403, detail="Account not approved")

    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=token)
