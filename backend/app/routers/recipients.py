from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from ..database import get_db
from ..models import Recipient
from ..schemas import RecipientCreate, RecipientUpdate, RecipientOut
from ..dependencies import get_approved_user
from ..models import User

router = APIRouter()


@router.get("", response_model=List[RecipientOut])
async def list_recipients(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_approved_user),
):
    result = await db.execute(select(Recipient).order_by(Recipient.name))
    return result.scalars().all()


@router.post("", response_model=RecipientOut, status_code=201)
async def create_recipient(
    data: RecipientCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_approved_user),
):
    r = Recipient(name=data.name)
    db.add(r)
    await db.commit()
    await db.refresh(r)
    return r


@router.put("/{rid}", response_model=RecipientOut)
async def update_recipient(
    rid: int,
    data: RecipientUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_approved_user),
):
    result = await db.execute(select(Recipient).where(Recipient.id == rid))
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Recipient not found")
    r.name = data.name
    await db.commit()
    await db.refresh(r)
    return r


@router.delete("/{rid}", status_code=204)
async def delete_recipient(
    rid: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_approved_user),
):
    result = await db.execute(select(Recipient).where(Recipient.id == rid))
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Recipient not found")
    await db.delete(r)
    await db.commit()
