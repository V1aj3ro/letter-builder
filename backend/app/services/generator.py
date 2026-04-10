"""
Generate a .docx letter.

Layout:
  Header (every page): logo left | org/IP details right + horizontal rule
  Footer (every page): banner image (if uploaded)
  Body:
    1. Meta line «Исх.№{number} от {date} г.»
    2. Recipient (right-aligned, bold)
    3. Subject (italic)
    4. Body (HTML)
    5. Signature table
    6. Executor block
"""
import os
from datetime import date as date_type
from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from lxml import etree

from .html_to_docx import html_to_docx

UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "/app/uploads")


def _clear_cell_borders(cell):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = OxmlElement("w:tcBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        tag = OxmlElement(f"w:{edge}")
        tag.set(qn("w:val"), "none")
        tag.set(qn("w:sz"), "0")
        tag.set(qn("w:space"), "0")
        tag.set(qn("w:color"), "auto")
        tcBorders.append(tag)
    tcPr.append(tcBorders)


def _add_paragraph_bottom_rule(paragraph):
    """Render paragraph with a bottom border — looks like <hr>."""
    pPr = paragraph._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "6")
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), "000000")
    pBdr.append(bottom)
    pPr.append(pBdr)


def _format_date(d) -> str:
    if isinstance(d, date_type):
        return d.strftime("%d.%m.%Y")
    return str(d)


def _emu_to_twips(emu: int) -> int:
    """Convert EMU to Word twips (dxa). 1 twip = 635 EMU."""
    return int(emu / 635)


def _build_header(section, org, sender_type: str):
    """
    Fill the section header with:
    - Left cell: logo image (flush to left page edge)
    - Right cell: org/IP details (8 pt, right-aligned)
    - Horizontal rule paragraph below the table
    """
    header = section.header
    header.is_linked_to_previous = False

    page_width = section.page_width
    logo_col = Cm(5.5)
    details_col = page_width - logo_col

    # --- Table (full page width, shifted left past the margin) ---
    htable = header.add_table(1, 2, page_width)
    tblPr = htable._tbl.find(qn("w:tblPr"))
    if tblPr is None:
        tblPr = OxmlElement("w:tblPr")
        htable._tbl.insert(0, tblPr)
    tblBorders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        tag = OxmlElement(f"w:{edge}")
        tag.set(qn("w:val"), "none")
        tblBorders.append(tag)
    tblPr.append(tblBorders)
    # Shift table to start at the left page edge (negative indent)
    tblInd = OxmlElement("w:tblInd")
    tblInd.set(qn("w:w"), str(-_emu_to_twips(section.left_margin)))
    tblInd.set(qn("w:type"), "dxa")
    tblPr.append(tblInd)

    left_cell = htable.cell(0, 0)
    right_cell = htable.cell(0, 1)
    _clear_cell_borders(left_cell)
    _clear_cell_borders(right_cell)

    left_cell.width  = logo_col
    right_cell.width = details_col

    # Left: logo
    left_para = left_cell.paragraphs[0]
    left_para.alignment = WD_ALIGN_PARAGRAPH.LEFT
    if org and org.logo_path and os.path.exists(org.logo_path):
        run = left_para.add_run()
        run.add_picture(org.logo_path, width=Cm(5.0))

    # Right: org or IP details
    right_para = right_cell.paragraphs[0]
    right_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    def _line(text: str, bold: bool = False):
        if not text:
            return
        run = right_para.add_run(("\n" if right_para.runs else "") + text)
        run.font.size = Pt(8)
        run.font.color.rgb = RGBColor(0, 0, 0)
        run.bold = bold

    if org:
        if sender_type == "ip":
            if org.ip_full_name:
                _line(org.ip_full_name, bold=True)
            if org.ip_inn:
                _line(f"ИНН {org.ip_inn}")
            if org.ip_ogrnip:
                _line(f"ОГРНИП {org.ip_ogrnip}")
            if org.ip_account:
                _line(f"Р/с {org.ip_account}")
            if org.ip_bank_name:
                _line(org.ip_bank_name)
            if org.ip_corr_account:
                _line(f"К/с {org.ip_corr_account}")
            if org.ip_bik:
                _line(f"БИК {org.ip_bik}")
            if org.ip_legal_address:
                _line(org.ip_legal_address)
            if org.ip_phone:
                _line(f"Тел.: {org.ip_phone}")
        else:
            if org.name:
                _line(org.name, bold=True)
            if org.inn:
                _line(f"ИНН {org.inn}")
            if org.ogrn:
                _line(f"ОГРН {org.ogrn}")
            if org.account:
                _line(f"Р/с {org.account}")
            if org.bank_name:
                _line(org.bank_name)
            if org.corr_account:
                _line(f"К/с {org.corr_account}")
            if org.bik:
                _line(f"БИК {org.bik}")
            if org.legal_address:
                _line(org.legal_address)
            if org.phone:
                _line(f"Тел.: {org.phone}")

    # Remove the default empty paragraph that header starts with
    # (it appears before our table — move it after as the rule)
    default_para = header.paragraphs[0]
    _add_paragraph_bottom_rule(default_para)
    # Move default paragraph to end (after the table)
    header._element.append(default_para._p)


def _build_footer(section, org):
    """Fill footer with the banner image spanning full content width."""
    if not (org and org.footer_banner_path and os.path.exists(org.footer_banner_path)):
        return

    footer = section.footer
    footer.is_linked_to_previous = False

    page_width = section.page_width

    para = footer.paragraphs[0]
    para.alignment = WD_ALIGN_PARAGRAPH.LEFT
    # Shift paragraph to start at left page edge and extend to right edge
    pPr = para._p.get_or_add_pPr()
    ind = OxmlElement("w:ind")
    ind.set(qn("w:left"),  str(-_emu_to_twips(section.left_margin)))
    ind.set(qn("w:right"), str(-_emu_to_twips(section.right_margin)))
    pPr.append(ind)
    run = para.add_run()
    run.add_picture(org.footer_banner_path, width=page_width)


async def generate_letter_docx(letter, org) -> str:
    output_dir = os.path.join(UPLOAD_DIR, "letters", str(letter.id))
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"letter_{letter.number}.docx")

    doc = Document()
    section = doc.sections[0]

    # Page margins
    section.top_margin = Cm(2.5)   # extra space for header
    section.bottom_margin = Cm(2.5)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(1.5)
    section.header_distance = Cm(0.5)
    section.footer_distance = Cm(0.5)

    # Default font
    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(12)

    sender = getattr(letter, "sender_type", "ooo")

    # Build header and footer
    _build_header(section, org, sender)
    _build_footer(section, org)

    # ── Meta line ────────────────────────────────────
    meta = doc.add_paragraph()
    meta.alignment = WD_ALIGN_PARAGRAPH.LEFT
    meta.add_run(f"Исх.№{letter.number} от {_format_date(letter.letter_date)} г.")

    # ── Recipient ────────────────────────────────────
    if letter.recipient:
        rec_para = doc.add_paragraph()
        rec_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        run = rec_para.add_run(letter.recipient.name)
        run.bold = True

    # ── Subject ──────────────────────────────────────
    if letter.subject:
        subj_para = doc.add_paragraph()
        subj_para.alignment = WD_ALIGN_PARAGRAPH.LEFT
        run = subj_para.add_run(letter.subject)
        run.italic = True

    doc.add_paragraph()

    # ── Body ─────────────────────────────────────────
    if letter.body:
        html_to_docx(letter.body, doc)

    doc.add_paragraph()

    # ── Signature ────────────────────────────────────
    sig_table = doc.add_table(rows=1, cols=3)
    for c in sig_table.cells[0:3] if False else sig_table.rows[0].cells:
        _clear_cell_borders(c)

    sig_table.columns[0].width = Cm(6)
    sig_table.columns[1].width = Cm(4)
    sig_table.columns[2].width = Cm(6)

    # Left
    sl = sig_table.cell(0, 0).paragraphs[0]
    sl.alignment = WD_ALIGN_PARAGRAPH.LEFT
    if sender == "ip":
        signer_role = org.ip_signer_role if org else ""
        signer_name_short = org.ip_full_name if org else ""
        short_name = f"ИП {signer_name_short}" if signer_name_short else ""
    else:
        signer_role = org.signer_role if org else ""
        short_name = org.short_name if org else ""

    left_text = "С уважением,"
    if signer_role:
        left_text += f"\n{signer_role}"
    if short_name:
        left_text += f" {short_name}"
    sl.add_run(left_text)

    # Middle: signature image
    sm = sig_table.cell(0, 1).paragraphs[0]
    sm.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if org and org.signature_path and os.path.exists(org.signature_path):
        run = sm.add_run()
        run.add_picture(org.signature_path, width=Cm(3))

    # Right: signer name
    sr = sig_table.cell(0, 2).paragraphs[0]
    sr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    if sender == "ip":
        signer_name = org.ip_signer_name if org else ""
    else:
        signer_name = org.signer_name if org else ""
    if signer_name:
        sr.add_run(signer_name)

    # ── Executor ─────────────────────────────────────
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
