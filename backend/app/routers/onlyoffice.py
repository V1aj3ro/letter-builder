"""
OnlyOffice Document Server integration.

Flow:
  1. Frontend: GET /api/onlyoffice/editor-config/{lid}
     → generates .docx from template, returns DocsAPI.DocEditor config
  2. Frontend inits the OnlyOffice editor (iframe) using that config
  3. OnlyOffice Document Server fetches the file:
     GET /api/onlyoffice/document/{lid}?token=<hmac>  (no user auth)
  4. User edits freely in Word-like UI
  5. OnlyOffice POSTs to /api/onlyoffice/callback/{lid} when saving (status 2/6)
     → backend downloads the modified .docx from OnlyOffice, saves as letter.docx_path
  6. Download endpoint serves letter.docx_path directly

Required env vars:
  ONLYOFFICE_SERVER   — base URL of OnlyOffice Document Server
                        default: https://office.demo.corpcore.ru
  APP_PUBLIC_URL      — public URL of THIS app reachable by OnlyOffice server
                        e.g. https://letters.demo.corpcore.ru  or  http://1.2.3.4:3010
  ONLYOFFICE_JWT_SECRET — JWT secret configured in OnlyOffice (optional)
"""
import hashlib
import hmac
import logging
import os
import time

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..database import get_db
from ..dependencies import get_approved_user
from ..models import Letter, Organization, User

log = logging.getLogger(__name__)
router = APIRouter()

ONLYOFFICE_SERVER = os.environ.get("ONLYOFFICE_SERVER", "https://office.demo.corpcore.ru")
APP_PUBLIC_URL = os.environ.get("APP_PUBLIC_URL", "").rstrip("/")
_DL_SECRET = os.environ.get("SECRET_KEY", "changeme")
ONLYOFFICE_JWT_SECRET = os.environ.get("ONLYOFFICE_JWT_SECRET", "")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _dl_token(letter_id: int) -> str:
    """Short HMAC token that lets OnlyOffice server download the document without user auth."""
    msg = f"dl:{letter_id}".encode()
    return hmac.new(_DL_SECRET.encode(), msg, hashlib.sha256).hexdigest()[:32]


def _verify_dl_token(letter_id: int, token: str) -> bool:
    return hmac.compare_digest(_dl_token(letter_id), token)


def _jwt_sign(payload: dict) -> str | None:
    """Sign the editor config with JWT if ONLYOFFICE_JWT_SECRET is set."""
    if not ONLYOFFICE_JWT_SECRET:
        return None
    try:
        import jwt as pyjwt  # pip install PyJWT
        return pyjwt.encode({"payload": payload}, ONLYOFFICE_JWT_SECRET, algorithm="HS256")
    except Exception as e:
        log.warning("OnlyOffice JWT signing failed: %s", e)
        return None


async def _get_letter_full(letter_id: int, db: AsyncSession) -> Letter:
    result = await db.execute(
        select(Letter)
        .options(
            selectinload(Letter.recipient),
            selectinload(Letter.creator),
            selectinload(Letter.project),
        )
        .where(Letter.id == letter_id)
    )
    letter = result.scalar_one_or_none()
    if not letter:
        raise HTTPException(status_code=404, detail="Letter not found")
    return letter


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/editor-config/{lid}")
async def get_editor_config(
    lid: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_approved_user),
):
    """
    Generate (or regenerate) the letter .docx and return the OnlyOffice editor config.
    Called by the frontend before opening the editor.
    """
    from ..services.generator import generate_letter_docx

    letter = await _get_letter_full(lid, db)

    org_result = await db.execute(select(Organization).where(Organization.id == 1))
    org = org_result.scalar_one_or_none()

    # (Re)generate the .docx — always fresh so form changes are reflected
    docx_path = await generate_letter_docx(letter, org)
    letter.docx_path = docx_path
    letter.pdf_path = None  # invalidate PDF cache
    await db.commit()

    base = APP_PUBLIC_URL
    if not base:
        log.warning(
            "APP_PUBLIC_URL is not set — OnlyOffice will not be able to fetch the document. "
            "Set APP_PUBLIC_URL to the public URL of this service."
        )

    token = _dl_token(lid)
    # Unique key per session — forces OnlyOffice to reload the document
    doc_key = f"letter_{lid}_{int(time.time())}"

    config = {
        "document": {
            "fileType": "docx",
            "key": doc_key,
            "title": f"Письмо №{letter.number}.docx",
            "url": f"{base}/api/onlyoffice/document/{lid}?token={token}",
            "permissions": {
                "edit": letter.status == "draft",
                "download": True,
                "print": True,
                "review": False,
            },
        },
        "documentType": "word",
        "editorConfig": {
            "callbackUrl": f"{base}/api/onlyoffice/callback/{lid}",
            "mode": "edit" if letter.status == "draft" else "view",
            "lang": "ru",
            "user": {
                "id": str(current_user.id),
                "name": current_user.full_name,
            },
            "customization": {
                "autosave": True,
                "forcesave": False,
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

    jwt_token = _jwt_sign(config)
    if jwt_token:
        config["token"] = jwt_token

    return {
        "server": ONLYOFFICE_SERVER,
        "config": config,
    }


@router.get("/document/{lid}")
async def serve_document(
    lid: int,
    token: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Serve the .docx file to OnlyOffice Document Server.
    Protected by HMAC token (no user session needed — OnlyOffice fetches this server-side).
    """
    if not _verify_dl_token(lid, token):
        raise HTTPException(status_code=403, detail="Invalid token")

    letter = await _get_letter_full(lid, db)

    if not letter.docx_path or not os.path.exists(letter.docx_path):
        raise HTTPException(status_code=404, detail="Document not found — generate it first")

    return FileResponse(
        letter.docx_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=f"letter_{letter.number}.docx",
    )


@router.post("/callback/{lid}")
async def onlyoffice_callback(
    lid: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Callback from OnlyOffice Document Server.
    status=1  — document is being edited (no action needed)
    status=2  — document ready for saving (all users left / timeout)
    status=3  — document saving error
    status=4  — document closed with no changes
    status=6  — force-save (triggered by user clicking Save or API call)
    status=7  — force-save error

    Must return {"error": 0} on success, or OnlyOffice will retry.
    """
    try:
        body = await request.json()
    except Exception:
        return {"error": 0}

    log.info("OnlyOffice callback letter_id=%s status=%s", lid, body.get("status"))

    status = body.get("status")
    if status in (2, 6):
        download_url = body.get("url")
        if not download_url:
            log.warning("OnlyOffice callback: no url in body for status %s", status)
            return {"error": 0}

        letter = await _get_letter_full(lid, db)

        # Determine output path
        if letter.docx_path:
            output_path = letter.docx_path
        else:
            from ..services.generator import UPLOAD_DIR
            out_dir = os.path.join(UPLOAD_DIR, "letters", str(lid))
            os.makedirs(out_dir, exist_ok=True)
            output_path = os.path.join(out_dir, f"letter_{letter.number}.docx")

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(download_url)
                resp.raise_for_status()
            with open(output_path, "wb") as f:
                f.write(resp.content)
            letter.docx_path = output_path
            letter.pdf_path = None  # invalidate cached PDF
            await db.commit()
            log.info("Letter %s saved from OnlyOffice (%d bytes)", lid, len(resp.content))
        except Exception as exc:
            log.error("Failed to save OnlyOffice document for letter %s: %s", lid, exc)
            return {"error": 1}

    return {"error": 0}
