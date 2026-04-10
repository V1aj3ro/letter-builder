"""
Generate a .docx letter following the reference template (р.docx).

Layout:
  1. Header table 1×2 (logo left | org details right)
  2. Horizontal rule paragraph
  3. Meta line: «Исх.№{number} от {date} г.»
  4. Recipient (right-aligned, bold)
  5. Subject (italic)
  6. Body (HTML via html_to_docx)
  7. Signature table 1×3
  8. Executor block
"""
import os
from datetime import date as date_type
from docx import Document
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

from .html_to_docx import html_to_docx

UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "/app/uploads")


def _set_cell_border(cell, **kwargs):
    """Set border on a table cell via XML."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = OxmlElement("w:tcBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        tag = OxmlElement(f"w:{edge}")
        tag.set(qn("w:val"), kwargs.get(edge, "none"))
        tag.set(qn("w:sz"), "0")
        tag.set(qn("w:space"), "0")
        tag.set(qn("w:color"), "auto")
        tcBorders.append(tag)
    tcPr.append(tcBorders)


def _add_horizontal_rule(document: Document):
    """Add a paragraph with a bottom border that renders as a horizontal line."""
    p = document.add_paragraph()
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "6")
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), "000000")
    pBdr.append(bottom)
    pPr.append(pBdr)
    return p


def _format_date(d) -> str:
    if isinstance(d, date_type):
        return d.strftime("%d.%m.%Y")
    return str(d)


async def generate_letter_docx(letter, org) -> str:
    """Build the .docx file and return its path."""
    output_dir = os.path.join(UPLOAD_DIR, "letters", str(letter.id))
    os.makedirs(output_dir, exist_ok=True)
    filename = f"letter_{letter.number}.docx"
    output_path = os.path.join(output_dir, filename)

    doc = Document()

    # Page margins: 2 cm top/bottom, 2.5 cm left, 1.5 cm right
    for section in doc.sections:
        section.top_margin = Cm(2)
        section.bottom_margin = Cm(2)
        section.left_margin = Cm(2.5)
        section.right_margin = Cm(1.5)

    # Default font
    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(12)

    # ──────────────────────────────────────────────────
    # 1. HEADER TABLE (logo | org details)
    # ──────────────────────────────────────────────────
    header_table = doc.add_table(rows=1, cols=2)
    header_table.style = "Table Grid"

    left_cell = header_table.cell(0, 0)
    right_cell = header_table.cell(0, 1)

    _set_cell_border(left_cell)
    _set_cell_border(right_cell)

    # Set column widths: logo ~5.5 cm, details ~10.5 cm
    header_table.columns[0].width = Cm(5.5)
    header_table.columns[1].width = Cm(10.5)

    # Left cell: logo
    left_para = left_cell.paragraphs[0]
    left_para.alignment = WD_ALIGN_PARAGRAPH.LEFT
    if org and org.logo_path and os.path.exists(org.logo_path):
        run = left_para.add_run()
        run.add_picture(org.logo_path, width=Cm(5.0))
    # else — leave empty

    # Right cell: org details
    right_para = right_cell.paragraphs[0]
    right_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

    def _details_run(text: str, bold: bool = False):
        run = right_para.add_run(text)
        run.font.size = Pt(8)
        run.bold = bold
        return run

    if org:
        lines = []
        if org.name:
            lines.append((org.name, True))
        if org.inn:
            lines.append((f"ИНН {org.inn}", False))
        if org.ogrn:
            lines.append((f"ОГРН {org.ogrn}", False))
        if org.account:
            lines.append((f"Р/с {org.account}", False))
        if org.bank_name:
            lines.append((f"{org.bank_name}", False))
        if org.corr_account:
            lines.append((f"К/с {org.corr_account}", False))
        if org.bik:
            lines.append((f"БИК {org.bik}", False))
        if org.legal_address:
            lines.append((f"{org.legal_address}", False))
        if org.phone:
            lines.append((f"Тел.: {org.phone}", False))

        for i, (text, bold) in enumerate(lines):
            if i > 0:
                right_para.add_run("\n").font.size = Pt(8)
            _details_run(text, bold=bold)

    # ──────────────────────────────────────────────────
    # 2. HORIZONTAL RULE
    # ──────────────────────────────────────────────────
    _add_horizontal_rule(doc)

    # ──────────────────────────────────────────────────
    # 3. META LINE
    # ──────────────────────────────────────────────────
    meta = doc.add_paragraph()
    meta.alignment = WD_ALIGN_PARAGRAPH.LEFT
    date_str = _format_date(letter.letter_date)
    meta.add_run(f"Исх.№{letter.number} от {date_str} г.")

    # ──────────────────────────────────────────────────
    # 4. RECIPIENT (right-aligned, bold)
    # ──────────────────────────────────────────────────
    if letter.recipient:
        rec_para = doc.add_paragraph()
        rec_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        run = rec_para.add_run(letter.recipient.name)
        run.bold = True

    # ──────────────────────────────────────────────────
    # 5. SUBJECT (italic)
    # ──────────────────────────────────────────────────
    if letter.subject:
        subj_para = doc.add_paragraph()
        subj_para.alignment = WD_ALIGN_PARAGRAPH.LEFT
        run = subj_para.add_run(letter.subject)
        run.italic = True

    # empty line before body
    doc.add_paragraph()

    # ──────────────────────────────────────────────────
    # 6. BODY
    # ──────────────────────────────────────────────────
    if letter.body:
        html_to_docx(letter.body, doc)

    # empty line before signature
    doc.add_paragraph()

    # ──────────────────────────────────────────────────
    # 7. SIGNATURE TABLE (role+org | signature image | signer name)
    # ──────────────────────────────────────────────────
    sig_table = doc.add_table(rows=1, cols=3)
    sig_table.style = "Table Grid"

    sig_left = sig_table.cell(0, 0)
    sig_mid = sig_table.cell(0, 1)
    sig_right = sig_table.cell(0, 2)

    for c in (sig_left, sig_mid, sig_right):
        _set_cell_border(c)

    sig_table.columns[0].width = Cm(6)
    sig_table.columns[1].width = Cm(4)
    sig_table.columns[2].width = Cm(6)

    # Left: role + short org name
    sig_left_para = sig_left.paragraphs[0]
    sig_left_para.alignment = WD_ALIGN_PARAGRAPH.LEFT
    left_text = "С уважением,"
    if org and org.signer_role:
        left_text += f"\n{org.signer_role}"
    if org and org.short_name:
        left_text += f" {org.short_name}"
    sig_left_para.add_run(left_text)

    # Middle: signature image
    sig_mid_para = sig_mid.paragraphs[0]
    sig_mid_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if org and org.signature_path and os.path.exists(org.signature_path):
        run = sig_mid_para.add_run()
        run.add_picture(org.signature_path, width=Cm(3))

    # Right: signer name
    sig_right_para = sig_right.paragraphs[0]
    sig_right_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    if org and org.signer_name:
        sig_right_para.add_run(org.signer_name)

    # ──────────────────────────────────────────────────
    # 8. EXECUTOR
    # ──────────────────────────────────────────────────
    doc.add_paragraph()
    exec_para = doc.add_paragraph()
    exec_text = "Исп.:"
    if letter.creator:
        exec_text += f"\n{letter.creator.full_name}"
        if letter.creator.phone:
            exec_text += f"\n{letter.creator.phone}"
    run = exec_para.add_run(exec_text)
    run.font.size = Pt(10)

    doc.save(output_path)
    return output_path
