import os
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from ..database import get_db
from ..models import Letter, Project, Recipient
from ..schemas import LetterCreate, LetterUpdate, LetterStatusUpdate, LetterOut
from ..dependencies import get_approved_user
from ..models import User

router = APIRouter()


async def _next_letter_number(db: AsyncSession) -> int:
    result = await db.execute(select(func.nextval("letter_number_seq")))
    return result.scalar()


async def _get_letter(letter_id: int, db: AsyncSession) -> Letter:
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


@router.get("", response_model=list[LetterOut])
async def list_letters(
    project_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_approved_user),
):
    result = await db.execute(
        select(Letter)
        .options(selectinload(Letter.recipient), selectinload(Letter.creator))
        .where(Letter.project_id == project_id)
        .order_by(Letter.number.desc())
    )
    return result.scalars().all()


@router.post("", response_model=LetterOut, status_code=201)
async def create_letter(
    data: LetterCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_approved_user),
):
    # Validate project exists
    proj_result = await db.execute(select(Project).where(Project.id == data.project_id))
    if not proj_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found")

    number = await _next_letter_number(db)
    letter = Letter(
        number=number,
        project_id=data.project_id,
        recipient_id=data.recipient_id,
        created_by=current_user.id,
        subject=data.subject,
        body=data.body,
        letter_date=data.letter_date or date.today(),
        sender_type=data.sender_type,
    )
    db.add(letter)
    await db.commit()
    await db.refresh(letter)
    return await _get_letter(letter.id, db)


@router.get("/{lid}", response_model=LetterOut)
async def get_letter(
    lid: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_approved_user),
):
    return await _get_letter(lid, db)


@router.put("/{lid}", response_model=LetterOut)
async def update_letter(
    lid: int,
    data: LetterUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_approved_user),
):
    letter = await _get_letter(lid, db)
    if letter.status != "draft":
        raise HTTPException(status_code=400, detail="Can only edit draft letters")

    if data.recipient_id is not None:
        letter.recipient_id = data.recipient_id
    if data.subject is not None:
        letter.subject = data.subject
    if data.body is not None:
        letter.body = data.body
    if data.letter_date is not None:
        letter.letter_date = data.letter_date
    if data.sender_type is not None:
        letter.sender_type = data.sender_type

    # Invalidate cached PDF (will be re-derived from current docx on next download)
    letter.pdf_path = None

    await db.commit()
    return await _get_letter(lid, db)


@router.delete("/{lid}", status_code=204)
async def delete_letter(
    lid: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_approved_user),
):
    letter = await _get_letter(lid, db)
    if letter.status != "draft":
        raise HTTPException(status_code=400, detail="Can only delete draft letters")
    await db.delete(letter)
    await db.commit()


@router.post("/{lid}/duplicate", response_model=LetterOut, status_code=201)
async def duplicate_letter(
    lid: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_approved_user),
):
    import shutil
    from ..services.generator import UPLOAD_DIR

    source = await _get_letter(lid, db)
    number = await _next_letter_number(db)

    new_letter = Letter(
        number=number,
        project_id=source.project_id,
        recipient_id=source.recipient_id,
        created_by=current_user.id,
        subject=source.subject,
        body=source.body,
        letter_date=source.letter_date,
        sender_type=source.sender_type,
        status="draft",
    )
    db.add(new_letter)
    await db.commit()
    await db.refresh(new_letter)

    # Copy docx file so the duplicate opens with the same content
    if source.docx_path and os.path.exists(source.docx_path):
        out_dir = os.path.join(UPLOAD_DIR, "letters", str(new_letter.id))
        os.makedirs(out_dir, exist_ok=True)
        new_docx = os.path.join(out_dir, f"letter_{number}.docx")
        shutil.copy2(source.docx_path, new_docx)
        new_letter.docx_path = new_docx
        await db.commit()

    return await _get_letter(new_letter.id, db)


@router.post("/{lid}/generate", response_model=LetterOut)
async def generate_letter(
    lid: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_approved_user),
):
    from ..services.generator import generate_letter_docx
    from ..services.pdf_converter import docx_to_pdf
    from sqlalchemy import select as sa_select
    from ..models import Organization

    letter = await _get_letter(lid, db)

    org_result = await db.execute(sa_select(Organization).where(Organization.id == 1))
    org = org_result.scalar_one_or_none()

    docx_path = await generate_letter_docx(letter, org)
    pdf_path = docx_to_pdf(docx_path)

    letter.docx_path = docx_path
    letter.pdf_path = pdf_path
    await db.commit()
    return await _get_letter(lid, db)


@router.get("/{lid}/download")
async def download_letter(
    lid: int,
    format: str = Query("pdf", regex="^(pdf|docx)$"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_approved_user),
):
    from ..services.generator import generate_letter_docx
    from ..services.pdf_converter import docx_to_pdf
    from sqlalchemy import select as sa_select
    from ..models import Organization

    letter = await _get_letter(lid, db)
    org_result = await db.execute(sa_select(Organization).where(Organization.id == 1))
    org = org_result.scalar_one_or_none()

    if format == "docx":
        if not letter.docx_path or not os.path.exists(letter.docx_path):
            docx_path = await generate_letter_docx(letter, org)
            letter.docx_path = docx_path
            await db.commit()
        return FileResponse(
            letter.docx_path,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=f"letter_{letter.number}.docx",
        )
    else:
        if not letter.pdf_path or not os.path.exists(letter.pdf_path):
            if not letter.docx_path or not os.path.exists(letter.docx_path):
                docx_path = await generate_letter_docx(letter, org)
                letter.docx_path = docx_path
                await db.commit()
            pdf_path = docx_to_pdf(letter.docx_path)
            letter.pdf_path = pdf_path
            await db.commit()
        return FileResponse(
            letter.pdf_path,
            media_type="application/pdf",
            filename=f"letter_{letter.number}.pdf",
        )


@router.patch("/{lid}/status", response_model=LetterOut)
async def update_status(
    lid: int,
    data: LetterStatusUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_approved_user),
):
    if data.status not in ("draft", "sent"):
        raise HTTPException(status_code=400, detail="Invalid status")
    letter = await _get_letter(lid, db)
    letter.status = data.status
    if data.status == "sent":
        letter.sent_at = datetime.utcnow()
    await db.commit()
    return await _get_letter(lid, db)
