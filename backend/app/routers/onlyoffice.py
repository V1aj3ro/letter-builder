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
import asyncio
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

# In-memory store: letter_id -> current doc_key (for forcesave command)
_active_doc_keys: dict[int, str] = {}

# Events to signal forcesave completion (letter_id -> Event)
_forcesave_events: dict[int, asyncio.Event] = {}

# Track last successful save time per letter (letter_id -> timestamp)
_last_saved_at: dict[int, float] = {}


async def ensure_letter_saved(lid: int, db: AsyncSession) -> bool:
    """
    Send forcesave to OnlyOffice and wait for callback (short timeout).
    Falls back to immediate return if OnlyOffice accepted the command.
    """
    doc_key = _active_doc_keys.get(lid)
    if not doc_key:
        return False  # No active editing session — serve whatever we have

    # Send forcesave command
    payload = {"c": "forcesave", "key": doc_key}
    jwt_token = _jwt_sign(payload)
    base_server = ONLYOFFICE_SERVER.rstrip("/")
    endpoints = [f"{base_server}/command", f"{base_server}/coauthoring/CommandService.ashx"]

    event = asyncio.Event()
    _forcesave_events[lid] = event
    callback_received = False

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            body = {"token": jwt_token} if jwt_token else payload
            last_err = None
            for url in endpoints:
                try:
                    resp = await client.post(url, json=body, headers={"Content-Type": "application/json"})
                    resp.raise_for_status()
                    result = resp.json()
                    error_code = result.get("error", 0)
                    if error_code in (0, 4):  # Accepted or no changes
                        log.info("ensure_letter_saved: OnlyOffice accepted (error=%d) for letter %s", error_code, lid)
                        break
                    last_err = Exception(f"OnlyOffice error {error_code}")
                    log.warning("ensure_letter_saved: OnlyOffice error %d for letter %s", error_code, lid)
                except httpx.HTTPError as exc:
                    last_err = exc
                    continue
            else:
                log.warning("ensure_letter_saved: all Command Service endpoints failed for letter %s", lid)
                return False

        # Wait briefly for callback (2s — enough if it's coming)
        try:
            await asyncio.wait_for(event.wait(), timeout=2.0)
            callback_received = True
        except asyncio.TimeoutError:
            # Callback may not come for forcesave with no changes — that's OK
            pass

        return True
    except Exception as exc:
        log.warning("ensure_letter_saved error for letter %s: %s", lid, exc)
        return False
    finally:
        _forcesave_events.pop(lid, None)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _dl_token(letter_id: int) -> str:
    """Short HMAC token that lets OnlyOffice server download the document without user auth."""
    msg = f"dl:{letter_id}".encode()
    return hmac.new(_DL_SECRET.encode(), msg, hashlib.sha256).hexdigest()[:32]


def _verify_dl_token(letter_id: int, token: str) -> bool:
    return hmac.compare_digest(_dl_token(letter_id), token)


def _hist_token(lid: int, ts: int) -> str:
    """HMAC token for serving a specific history version file."""
    msg = f"hist:{lid}:{ts}".encode()
    return hmac.new(_DL_SECRET.encode(), msg, hashlib.sha256).hexdigest()[:32]


def _save_version(lid: int, current_path: str) -> None:
    """Copy current docx to versions dir and update meta.json before overwrite."""
    import json
    import shutil
    from ..services.generator import UPLOAD_DIR

    versions_dir = os.path.join(UPLOAD_DIR, "letters", str(lid), "versions")
    os.makedirs(versions_dir, exist_ok=True)

    meta_path = os.path.join(versions_dir, "meta.json")
    meta: list = []
    if os.path.exists(meta_path):
        try:
            with open(meta_path) as f:
                meta = json.load(f)
        except Exception:
            meta = []

    ts = int(time.time())
    version_num = len(meta) + 1
    filename = f"v{version_num}_{ts}.docx"
    dest = os.path.join(versions_dir, filename)

    try:
        shutil.copy2(current_path, dest)
    except Exception as e:
        log.warning("Could not save version snapshot: %s", e)
        return

    meta.append({
        "version": version_num,
        "ts": ts,
        "created": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts)),
        "file": filename,
    })
    with open(meta_path, "w") as f:
        json.dump(meta, f)
    log.info("Saved version %d for letter %d", version_num, lid)


def _jwt_sign(payload: dict) -> str | None:
    """Sign the editor config with JWT if ONLYOFFICE_JWT_SECRET is set."""
    if not ONLYOFFICE_JWT_SECRET:
        return None
    try:
        from jose import jwt as jose_jwt
        return jose_jwt.encode(payload, ONLYOFFICE_JWT_SECRET, algorithm="HS256")
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
    regenerate: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_approved_user),
):
    """
    Return the OnlyOffice editor config for a letter.
    Regenerates the .docx only when:
      - regenerate=true (form fields changed, explicit request from frontend)
      - no .docx file exists yet (first open)
    Otherwise serves the existing file so OnlyOffice edits are preserved.
    """
    from ..services.generator import generate_letter_docx

    letter = await _get_letter_full(lid, db)

    org_result = await db.execute(select(Organization).where(Organization.id == 1))
    org = org_result.scalar_one_or_none()

    need_regen = regenerate or not letter.docx_path or not os.path.exists(letter.docx_path)
    if need_regen:
        docx_path = await generate_letter_docx(letter, org)
        letter.docx_path = docx_path
        letter.pdf_path = None
        await db.commit()

    base = APP_PUBLIC_URL
    if not base:
        log.warning(
            "APP_PUBLIC_URL is not set — OnlyOffice will not be able to fetch the document. "
            "Set APP_PUBLIC_URL to the public URL of this service."
        )

    token = _dl_token(lid)
    # Use stable key for forcesave via Command Service.
    # Change key only on regeneration so OnlyOffice reloads the document.
    if need_regen:
        doc_key = f"letter_{lid}_regen_{int(time.time())}"
    else:
        doc_key = f"letter_{lid}"
    _active_doc_keys[lid] = doc_key

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


def _verify_jwt_callback(request: Request, body: dict) -> bool:
    """Verify JWT sent by OnlyOffice in the Authorization header or body token."""
    if not ONLYOFFICE_JWT_SECRET:
        return True  # JWT disabled on OnlyOffice side — skip verification
    try:
        from jose import jwt as jose_jwt, JWTError
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            token = auth[7:]
        else:
            token = body.get("token", "")
        if not token:
            log.warning("OnlyOffice callback: no JWT token, rejecting")
            return False
        jose_jwt.decode(token, ONLYOFFICE_JWT_SECRET, algorithms=["HS256"])
        return True
    except Exception as e:
        log.warning("OnlyOffice callback JWT verification failed: %s", e)
        return False


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

    if not _verify_jwt_callback(request, body):
        raise HTTPException(status_code=403, detail="Invalid OnlyOffice JWT")

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
            # Snapshot current version before overwriting
            if os.path.exists(output_path):
                _save_version(lid, output_path)
            with open(output_path, "wb") as f:
                f.write(resp.content)
            letter.docx_path = output_path
            letter.pdf_path = None  # invalidate cached PDF
            await db.commit()
            log.info("Letter %s saved from OnlyOffice (%d bytes)", lid, len(resp.content))

            # Record save timestamp
            _last_saved_at[lid] = time.time()

            # Signal forcesave completion if someone is waiting
            if status == 6 and lid in _forcesave_events:
                _forcesave_events[lid].set()
        except Exception as exc:
            log.error("Failed to save OnlyOffice document for letter %s: %s", lid, exc)

            # Signal error for forcesave waiters
            if status == 6 and lid in _forcesave_events:
                _forcesave_events[lid].set()
            return {"error": 1}

    return {"error": 0}


@router.post("/forcesave/{lid}")
async def forcesave(
    lid: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_approved_user),
):
    """
    Send forcesave command to OnlyOffice Command Service.
    Waits for the callback to complete before returning (timeout 15s).
    """
    await _get_letter_full(lid, db)  # 404 check

    doc_key = _active_doc_keys.get(lid)
    if not doc_key:
        raise HTTPException(status_code=400, detail="No active editing session for this letter")

    # Build Command Service payload
    payload = {"c": "forcesave", "key": doc_key}

    # Sign with JWT if OnlyOffice has JWT enabled
    jwt_token = _jwt_sign(payload)

    # Try modern /command endpoint (v8.2+), fallback to legacy /coauthoring/CommandService.ashx
    base_server = ONLYOFFICE_SERVER.rstrip("/")
    endpoints = [f"{base_server}/command", f"{base_server}/coauthoring/CommandService.ashx"]

    # Create event to wait for callback completion
    event = asyncio.Event()
    _forcesave_events[lid] = event

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            body: dict
            if jwt_token:
                body = {"token": jwt_token}
            else:
                body = payload

            last_err: Exception | None = None
            for url in endpoints:
                try:
                    resp = await client.post(
                        url,
                        json=body,
                        headers={"Content-Type": "application/json"},
                    )
                    resp.raise_for_status()
                    result = resp.json()
                    error_code = result.get("error", 0)
                    log.info("OnlyOffice Command Service response: %s", result)
                    if error_code == 0:
                        break  # Success — will wait for callback
                    if error_code == 4:
                        # No changes to save — but we still need to ensure file is saved
                        log.info("Forcesave: no changes for letter %s, waiting for callback to confirm", lid)
                        break  # Proceed to wait for callback (may have already been saved)
                    error_messages = {
                        1: "Document key not found (check _active_doc_keys)",
                        2: "Invalid callback URL",
                        3: "Internal server error",
                        5: "Invalid command",
                        6: "Invalid token",
                    }
                    msg = error_messages.get(error_code, f"Unknown error {error_code}")
                    log.error("OnlyOffice forcesave error %d for letter %s: %s", error_code, lid, msg)
                    raise HTTPException(status_code=400, detail=f"OnlyOffice forcesave error: {msg}")
                    break
                except httpx.HTTPError as exc:
                    last_err = exc
                    log.debug("OnlyOffice Command Service failed at %s: %s", url, exc)
                    continue
                except HTTPException:
                    raise
            else:
                raise last_err or Exception("All Command Service endpoints failed")

        # Wait for callback to complete (15s timeout)
        log.info("Waiting for forcesave callback for letter %s", lid)
        try:
            await asyncio.wait_for(event.wait(), timeout=15.0)
            return {"status": "ok", "saved": True, "reason": "callback_received"}
        except asyncio.TimeoutError:
            log.warning("Forcesave callback timeout for letter %s", lid)
            return {"status": "ok", "saved": False, "reason": "callback_timeout"}
    finally:
        _forcesave_events.pop(lid, None)


@router.get("/save-status/{lid}")
async def get_save_status(
    lid: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_approved_user),
):
    """
    Check if the OnlyOffice document has been saved.
    Returns the last save timestamp and file mtime.
    """
    letter = await _get_letter_full(lid, db)

    saved_at = _last_saved_at.get(lid)
    file_mtime = None
    if letter.docx_path and os.path.exists(letter.docx_path):
        file_mtime = os.path.getmtime(letter.docx_path)

    return {
        "saved_at": saved_at,
        "file_mtime": file_mtime,
    }


@router.get("/history/{lid}")
async def get_history(
    lid: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_approved_user),
):
    """Return OnlyOffice-compatible history list for a letter."""
    import json
    from ..services.generator import UPLOAD_DIR

    await _get_letter_full(lid, db)  # 404 check
    versions_dir = os.path.join(UPLOAD_DIR, "letters", str(lid), "versions")
    meta_path = os.path.join(versions_dir, "meta.json")

    if not os.path.exists(meta_path):
        return {"currentVersion": 1, "history": []}

    with open(meta_path) as f:
        meta = json.load(f)

    history = [
        {
            "version": e["version"],
            "created": e["created"],
            "user": {"id": "0", "name": ""},
            "serverVersion": "7.0.0",
        }
        for e in meta
    ]
    return {"currentVersion": len(meta) + 1, "history": history}


@router.get("/history-data/{lid}/{version}")
async def get_history_data(
    lid: int,
    version: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_approved_user),
):
    """Return URL for a specific history version (called by OnlyOffice editor)."""
    import json
    from ..services.generator import UPLOAD_DIR

    versions_dir = os.path.join(UPLOAD_DIR, "letters", str(lid), "versions")
    meta_path = os.path.join(versions_dir, "meta.json")
    if not os.path.exists(meta_path):
        raise HTTPException(status_code=404, detail="No history")

    with open(meta_path) as f:
        meta = json.load(f)

    entry = next((e for e in meta if e["version"] == version), None)
    if not entry:
        raise HTTPException(status_code=404, detail="Version not found")

    base = APP_PUBLIC_URL
    token = _hist_token(lid, entry["ts"])
    result: dict = {
        "version": version,
        "url": f"{base}/api/onlyoffice/history-file/{lid}/{entry['ts']}?token={token}",
    }
    # Provide previous version URL for diff display
    prev = next((e for e in meta if e["version"] == version - 1), None)
    if prev:
        prev_token = _hist_token(lid, prev["ts"])
        result["urlPrev"] = f"{base}/api/onlyoffice/history-file/{lid}/{prev['ts']}?token={prev_token}"

    return result


@router.get("/history-file/{lid}/{ts}")
async def get_history_file(
    lid: int,
    ts: int,
    token: str,
    db: AsyncSession = Depends(get_db),
):
    """Serve a specific version file to OnlyOffice (HMAC-protected, no user auth)."""
    import json
    from ..services.generator import UPLOAD_DIR

    if not hmac.compare_digest(_hist_token(lid, ts), token):
        raise HTTPException(status_code=403, detail="Invalid token")

    versions_dir = os.path.join(UPLOAD_DIR, "letters", str(lid), "versions")
    meta_path = os.path.join(versions_dir, "meta.json")
    if not os.path.exists(meta_path):
        raise HTTPException(status_code=404, detail="No history")

    with open(meta_path) as f:
        meta = json.load(f)

    entry = next((e for e in meta if e["ts"] == ts), None)
    if not entry:
        raise HTTPException(status_code=404, detail="Version not found")

    file_path = os.path.join(versions_dir, entry["file"])
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Version file not found")

    return FileResponse(
        file_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=f"letter_{lid}_v{entry['version']}.docx",
    )
