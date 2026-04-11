import hashlib
import hmac as hmac_module
import logging
import os
import time
import uuid

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..database import get_db
from ..models import Organization
from ..schemas import OrganizationOut, OrganizationUpdate
from ..dependencies import get_approved_user, get_admin_user
from ..models import User

log = logging.getLogger(__name__)

ONLYOFFICE_SERVER    = os.environ.get("ONLYOFFICE_SERVER", "https://office.demo.corpcore.ru")
APP_PUBLIC_URL       = os.environ.get("APP_PUBLIC_URL", "").rstrip("/")
_TPL_SECRET          = os.environ.get("SECRET_KEY", "changeme")
ONLYOFFICE_JWT_SECRET = os.environ.get("ONLYOFFICE_JWT_SECRET", "")


def _tpl_token(ttype: str) -> str:
    msg = f"tpl:{ttype}".encode()
    return hmac_module.new(_TPL_SECRET.encode(), msg, hashlib.sha256).hexdigest()[:32]


def _tpl_jwt_sign(payload: dict) -> str | None:
    if not ONLYOFFICE_JWT_SECRET:
        return None
    try:
        from jose import jwt as jose_jwt
        return jose_jwt.encode(payload, ONLYOFFICE_JWT_SECRET, algorithm="HS256")
    except Exception as e:
        log.warning("Template JWT signing failed: %s", e)
        return None

router = APIRouter()

UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "/app/uploads")
ALLOWED_LOGO     = {"image/png", "image/jpeg", "image/svg+xml"}
ALLOWED_SIG      = {"image/png", "image/jpeg"}
ALLOWED_TEMPLATE = {
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/octet-stream",  # некоторые браузеры отправляют .docx без MIME
}


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


@router.post("/footer-banner", response_model=OrganizationOut)
async def upload_footer_banner(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_admin_user),
):
    if file.content_type not in ALLOWED_LOGO:
        raise HTTPException(status_code=400, detail="Invalid file type for footer banner")

    org = await _get_or_create_org(db)

    if org.footer_banner_path and os.path.exists(org.footer_banner_path):
        os.remove(org.footer_banner_path)

    ext = file.filename.rsplit(".", 1)[-1] if "." in file.filename else "png"
    filename = f"{uuid.uuid4()}.{ext}"
    path = os.path.join(UPLOAD_DIR, "org", filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)

    content = await file.read()
    with open(path, "wb") as f:
        f.write(content)

    org.footer_banner_path = path
    await db.commit()
    await db.refresh(org)
    return org


async def _save_docx_upload(file: UploadFile, old_path: str | None) -> str:
    """Validate, save a .docx upload and return the new file path."""
    if file.content_type not in ALLOWED_TEMPLATE and not file.filename.endswith(".docx"):
        raise HTTPException(status_code=400, detail="Требуется файл .docx")
    if old_path and os.path.exists(old_path):
        os.remove(old_path)
    filename = f"{uuid.uuid4()}.docx"
    path = os.path.join(UPLOAD_DIR, "org", filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    content = await file.read()
    with open(path, "wb") as f:
        f.write(content)
    return path


@router.post("/template-ooo", response_model=OrganizationOut)
async def upload_template_ooo(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_admin_user),
):
    org = await _get_or_create_org(db)
    org.template_ooo_path = await _save_docx_upload(file, org.template_ooo_path)
    await db.commit()
    await db.refresh(org)
    return org


@router.post("/template-ip", response_model=OrganizationOut)
async def upload_template_ip(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_admin_user),
):
    org = await _get_or_create_org(db)
    org.template_ip_path = await _save_docx_upload(file, org.template_ip_path)
    await db.commit()
    await db.refresh(org)
    return org


# ── Template OnlyOffice editor ────────────────────────────────────────────────

@router.get("/template-config/{ttype}")
async def get_template_editor_config(
    ttype: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    if ttype not in ("ooo", "ip"):
        raise HTTPException(status_code=400, detail="ttype must be 'ooo' or 'ip'")
    org = await _get_or_create_org(db)
    tpl_path = org.template_ooo_path if ttype == "ooo" else org.template_ip_path
    if not tpl_path or not os.path.exists(tpl_path):
        raise HTTPException(status_code=404, detail="Шаблон не загружен — сначала загрузите .docx файл")

    base = APP_PUBLIC_URL
    token = _tpl_token(ttype)
    doc_key = f"template_{ttype}_{int(time.time())}"
    title = "Шаблон ООО.docx" if ttype == "ooo" else "Шаблон ИП.docx"

    config = {
        "document": {
            "fileType": "docx",
            "key": doc_key,
            "title": title,
            "url": f"{base}/api/organization/template-document/{ttype}?token={token}",
            "permissions": {"edit": True, "download": True, "print": True, "review": False},
        },
        "documentType": "word",
        "editorConfig": {
            "callbackUrl": f"{base}/api/organization/template-callback/{ttype}",
            "mode": "edit",
            "lang": "ru",
            "user": {"id": str(current_user.id), "name": current_user.full_name},
            "customization": {
                "autosave": True,
                "forcesave": True,
                "logo": {"visible": False},
                "chat": {"visible": False},
                "feedback": {"visible": False},
                "help": {"visible": False},
                "hideRightMenu": True,
                "toolbarNoTabs": False,
                "zoom": 100,
            },
        },
    }
    jwt_token = _tpl_jwt_sign(config)
    if jwt_token:
        config["token"] = jwt_token
    return {"server": ONLYOFFICE_SERVER, "config": config}


@router.get("/template-document/{ttype}")
async def serve_template_document(
    ttype: str,
    token: str,
    db: AsyncSession = Depends(get_db),
):
    if ttype not in ("ooo", "ip"):
        raise HTTPException(status_code=400, detail="Invalid ttype")
    if not hmac_module.compare_digest(_tpl_token(ttype), token):
        raise HTTPException(status_code=403, detail="Invalid token")
    org = await _get_or_create_org(db)
    tpl_path = org.template_ooo_path if ttype == "ooo" else org.template_ip_path
    if not tpl_path or not os.path.exists(tpl_path):
        raise HTTPException(status_code=404, detail="Template not found")
    return FileResponse(
        tpl_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=f"template_{ttype}.docx",
    )


@router.post("/template-callback/{ttype}")
async def template_callback(
    ttype: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    if ttype not in ("ooo", "ip"):
        raise HTTPException(status_code=400, detail="Invalid ttype")
    try:
        body = await request.json()
    except Exception:
        return {"error": 0}

    # JWT verification
    if ONLYOFFICE_JWT_SECRET:
        try:
            from jose import jwt as jose_jwt
            auth_hdr = request.headers.get("Authorization", "")
            tok = auth_hdr[7:] if auth_hdr.startswith("Bearer ") else body.get("token", "")
            if tok:
                jose_jwt.decode(tok, ONLYOFFICE_JWT_SECRET, algorithms=["HS256"])
        except Exception as e:
            log.warning("Template callback JWT failed: %s", e)
            raise HTTPException(status_code=403, detail="Invalid JWT")

    status = body.get("status")
    if status in (2, 6):
        download_url = body.get("url")
        if not download_url:
            return {"error": 0}
        org = await _get_or_create_org(db)
        tpl_path = org.template_ooo_path if ttype == "ooo" else org.template_ip_path
        if not tpl_path:
            return {"error": 0}
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(download_url)
                resp.raise_for_status()
            with open(tpl_path, "wb") as f:
                f.write(resp.content)
            log.info("Template %s saved from OnlyOffice (%d bytes)", ttype, len(resp.content))
        except Exception as exc:
            log.error("Failed to save template %s: %s", ttype, exc)
            return {"error": 1}
    return {"error": 0}
