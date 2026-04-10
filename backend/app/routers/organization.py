import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..database import get_db
from ..models import Organization
from ..schemas import OrganizationOut, OrganizationUpdate
from ..dependencies import get_approved_user, get_admin_user
from ..models import User

router = APIRouter()

UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "/app/uploads")
ALLOWED_LOGO = {"image/png", "image/jpeg", "image/svg+xml"}
ALLOWED_SIG = {"image/png", "image/jpeg"}


async def _get_or_create_org(db: AsyncSession) -> Organization:
    result = await db.execute(select(Organization).where(Organization.id == 1))
    org = result.scalar_one_or_none()
    if not org:
        org = Organization(id=1)
        db.add(org)
        await db.commit()
        await db.refresh(org)
    return org


@router.get("", response_model=OrganizationOut)
async def get_organization(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_approved_user),
):
    return await _get_or_create_org(db)


@router.put("", response_model=OrganizationOut)
async def update_organization(
    data: OrganizationUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_admin_user),
):
    org = await _get_or_create_org(db)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(org, field, value)
    await db.commit()
    await db.refresh(org)
    return org


@router.post("/logo", response_model=OrganizationOut)
async def upload_logo(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_admin_user),
):
    if file.content_type not in ALLOWED_LOGO:
        raise HTTPException(status_code=400, detail="Invalid file type for logo")

    org = await _get_or_create_org(db)

    # Delete old file
    if org.logo_path and os.path.exists(org.logo_path):
        os.remove(org.logo_path)

    ext = file.filename.rsplit(".", 1)[-1] if "." in file.filename else "png"
    filename = f"{uuid.uuid4()}.{ext}"
    path = os.path.join(UPLOAD_DIR, "org", filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)

    content = await file.read()
    with open(path, "wb") as f:
        f.write(content)

    org.logo_path = path
    await db.commit()
    await db.refresh(org)
    return org


@router.post("/signature", response_model=OrganizationOut)
async def upload_signature(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_admin_user),
):
    if file.content_type not in ALLOWED_SIG:
        raise HTTPException(status_code=400, detail="Invalid file type for signature")

    org = await _get_or_create_org(db)

    if org.signature_path and os.path.exists(org.signature_path):
        os.remove(org.signature_path)

    ext = file.filename.rsplit(".", 1)[-1] if "." in file.filename else "png"
    filename = f"{uuid.uuid4()}.{ext}"
    path = os.path.join(UPLOAD_DIR, "org", filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)

    content = await file.read()
    with open(path, "wb") as f:
        f.write(content)

    org.signature_path = path
    await db.commit()
    await db.refresh(org)
    return org
