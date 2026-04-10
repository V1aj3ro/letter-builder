from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from ..database import get_db
from ..models import Project, ProjectRecipient, Recipient, Letter
from ..schemas import (
    ProjectCreate, ProjectUpdate, ProjectOut, ProjectDetailOut,
    ProjectRecipientAdd, DefaultRecipientUpdate,
)
from ..dependencies import get_approved_user, get_admin_user
from ..models import User

router = APIRouter()


@router.get("", response_model=list[ProjectOut])
async def list_projects(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_approved_user),
):
    result = await db.execute(
        select(Project)
        .options(selectinload(Project.default_recipient))
        .order_by(Project.created_at.desc())
    )
    projects = result.scalars().all()

    out = []
    for p in projects:
        count_result = await db.execute(
            select(func.count()).select_from(Letter).where(Letter.project_id == p.id)
        )
        count = count_result.scalar()
        d = ProjectOut.model_validate(p)
        d.letter_count = count
        out.append(d)
    return out


@router.post("", response_model=ProjectOut, status_code=201)
async def create_project(
    data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_approved_user),
):
    p = Project(name=data.name, created_by=current_user.id)
    db.add(p)
    await db.commit()
    await db.refresh(p)
    d = ProjectOut.model_validate(p)
    d.letter_count = 0
    return d


@router.get("/{pid}", response_model=ProjectDetailOut)
async def get_project(
    pid: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_approved_user),
):
    result = await db.execute(
        select(Project)
        .options(
            selectinload(Project.default_recipient),
            selectinload(Project.recipient_links).selectinload(ProjectRecipient.recipient),
        )
        .where(Project.id == pid)
    )
    p = result.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")

    out = ProjectDetailOut.model_validate(p)
    out.recipients = [link.recipient for link in p.recipient_links]
    return out


@router.put("/{pid}", response_model=ProjectOut)
async def update_project(
    pid: int,
    data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_approved_user),
):
    result = await db.execute(select(Project).where(Project.id == pid))
    p = result.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    p.name = data.name
    await db.commit()
    await db.refresh(p)
    count_result = await db.execute(
        select(func.count()).select_from(Letter).where(Letter.project_id == p.id)
    )
    d = ProjectOut.model_validate(p)
    d.letter_count = count_result.scalar()
    return d


@router.delete("/{pid}", status_code=204)
async def delete_project(
    pid: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_admin_user),
):
    result = await db.execute(select(Project).where(Project.id == pid))
    p = result.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    await db.delete(p)
    await db.commit()


@router.post("/{pid}/recipients", status_code=201)
async def add_project_recipient(
    pid: int,
    data: ProjectRecipientAdd,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_approved_user),
):
    result = await db.execute(select(Project).where(Project.id == pid))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found")

    existing = await db.execute(
        select(ProjectRecipient).where(
            ProjectRecipient.project_id == pid,
            ProjectRecipient.recipient_id == data.recipient_id,
        )
    )
    if existing.scalar_one_or_none():
        return {"message": "already exists"}

    link = ProjectRecipient(project_id=pid, recipient_id=data.recipient_id)
    db.add(link)
    await db.commit()
    return {"message": "added"}


@router.delete("/{pid}/recipients/{rid}", status_code=204)
async def remove_project_recipient(
    pid: int,
    rid: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_approved_user),
):
    result = await db.execute(
        select(ProjectRecipient).where(
            ProjectRecipient.project_id == pid,
            ProjectRecipient.recipient_id == rid,
        )
    )
    link = result.scalar_one_or_none()
    if not link:
        raise HTTPException(status_code=404, detail="Not found")
    await db.delete(link)
    await db.commit()


@router.put("/{pid}/default-recipient")
async def set_default_recipient(
    pid: int,
    data: DefaultRecipientUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_approved_user),
):
    result = await db.execute(select(Project).where(Project.id == pid))
    p = result.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")

    # Verify recipient exists
    rec_result = await db.execute(select(Recipient).where(Recipient.id == data.recipient_id))
    if not rec_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Recipient not found")

    p.default_recipient_id = data.recipient_id
    await db.commit()
    return {"message": "updated"}
