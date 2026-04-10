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
from docx.shared import Cm, Pt, Twips, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

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


def _clear_paragraph_borders(paragraph):
    """Explicitly set all paragraph borders to none (prevents style inheritance)."""
    pPr = paragraph._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    for edge in ("top", "left", "bottom", "right", "between", "bar"):
        tag = OxmlElement(f"w:{edge}")
        tag.set(qn("w:val"), "none")
        pBdr.append(tag)
    pPr.append(pBdr)


def _set_cell_valign_center(cell):
    """Vertically center content inside a table cell."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    vAlign = OxmlElement("w:vAlign")
    vAlign.set(qn("w:val"), "center")
    tcPr.append(vAlign)


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

    # Left: logo — vertically centered
    _set_cell_valign_center(left_cell)
    left_para = left_cell.paragraphs[0]
    left_para.alignment = WD_ALIGN_PARAGRAPH.LEFT
    _clear_paragraph_borders(left_para)
    if org and org.logo_path and os.path.exists(org.logo_path):
        run = left_para.add_run()
        run.add_picture(org.logo_path, width=Cm(5.87), height=Cm(3.13))

    # Right: org or IP details
    right_para = right_cell.paragraphs[0]
    right_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    _clear_paragraph_borders(right_para)

    def _line(text: str, bold: bool = False):
        if not text:
            return
        run = right_para.add_run(("\n" if right_para.runs else "") + text)
        run.font.name = "Roboto"
        run.font.size = Pt(11)
        run.font.color.rgb = RGBColor(0x15, 0x15, 0x15)
        run.bold = bold

    if org:
        if sender_type == "ip":
            if org.ip_full_name:
                _line(org.ip_full_name)
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
                _line(org.name)
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

    # Move the default empty paragraph to after the table
    default_para = header.paragraphs[0]
    _clear_paragraph_borders(default_para)
    header._element.append(default_para._p)


def _build_footer(section, org):
    """
    Fill footer with an ANCHORED banner image (like the reference document).

    Using wp:anchor + wrapNone means the paragraph itself has near-zero height,
    so the footer zone stays minimal.  The image floats at the page bottom.
    """
    if not (org and org.footer_banner_path and os.path.exists(org.footer_banner_path)):
        return

    footer = section.footer
    footer.is_linked_to_previous = False

    para = footer.paragraphs[0]
    para.alignment = WD_ALIGN_PARAGRAPH.LEFT

    # Collapse the paragraph to near-zero height via XML spacing
    pPr = para._p.get_or_add_pPr()
    sp_elem = OxmlElement("w:spacing")
    sp_elem.set(qn("w:before"), "0")
    sp_elem.set(qn("w:after"),  "0")
    pPr.append(sp_elem)

    # ── Step 1: add picture inline so python-docx registers the relationship ──
    run = para.add_run()
    run.add_picture(org.footer_banner_path, width=Cm(20.97), height=Cm(3.79))

    # ── Step 2: convert the inline drawing to an anchored (floating) drawing ──
    r_elem  = run._r
    drawing = r_elem.find(qn("w:drawing"))
    if drawing is None:
        return
    inline = drawing.find(qn("wp:inline"))
    if inline is None:
        return

    # Grab child elements we need to transplant
    extent  = inline.find(qn("wp:extent"))
    effect  = inline.find(qn("wp:effectExtent"))
    docPr   = inline.find(qn("wp:docPr"))
    cNvGFP  = inline.find(qn("wp:cNvGraphicFramePr"))
    graphic = inline.find(qn("a:graphic"))

    # Build the anchor element (matches reference doc structure)
    anchor = OxmlElement("wp:anchor")
    anchor.set("distT", "0")
    anchor.set("distB", "0")
    anchor.set("distL", "0")
    anchor.set("distR", "0")
    anchor.set("simplePos",    "0")
    anchor.set("relativeHeight", "251653120")
    anchor.set("behindDoc",    "0")
    anchor.set("locked",       "0")
    anchor.set("layoutInCell", "1")
    anchor.set("allowOverlap", "0")

    # Required simplePos placeholder
    sp_pos = OxmlElement("wp:simplePos")
    sp_pos.set("x", "0"); sp_pos.set("y", "0")
    anchor.append(sp_pos)

    # Horizontal: shift left by left_margin (EMU) so image starts at page edge
    posH = OxmlElement("wp:positionH")
    posH.set("relativeFrom", "column")
    oh = OxmlElement("wp:posOffset")
    oh.text = str(-int(section.left_margin))   # section.left_margin is in EMU
    posH.append(oh)
    anchor.append(posH)

    # Vertical: start at the top of the footer paragraph
    posV = OxmlElement("wp:positionV")
    posV.set("relativeFrom", "paragraph")
    ov = OxmlElement("wp:posOffset")
    ov.text = "0"
    posV.append(ov)
    anchor.append(posV)

    # Transplant inline children in OOXML-required order:
    # extent → effectExtent → wrapNone → docPr → cNvGraphicFramePr → graphic
    for child in (extent, effect):
        if child is not None:
            anchor.append(child)

    wn = OxmlElement("wp:wrapNone")
    anchor.append(wn)

    for child in (docPr, cNvGFP, graphic):
        if child is not None:
            anchor.append(child)

    # Swap inline ↔ anchor
    drawing.remove(inline)
    drawing.append(anchor)


async def generate_letter_docx(letter, org) -> str:
    output_dir = os.path.join(UPLOAD_DIR, "letters", str(letter.id))
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"letter_{letter.number}.docx")

    doc = Document()
    section = doc.sections[0]

    # Page margins — match reference document (twips from original XML)
    section.top_margin    = Twips(1360)   # 2.41 cm
    section.bottom_margin = Twips(0)      # 0 — footer sticks to page edge
    section.left_margin   = Twips(1276)   # 2.26 cm
    section.right_margin  = Twips(707)    # 1.25 cm
    section.header_distance = Twips(720)  # 1.27 cm
    section.footer_distance = Twips(291)  # 0.51 cm

    # Default font and paragraph spacing
    style = doc.styles["Normal"]
    style.font.name = "Roboto"
    style.font.size = Pt(11)
    style.paragraph_format.space_before = Pt(0)
    style.paragraph_format.space_after  = Pt(6)
    style.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE

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
        run.font.name = "Roboto"
        run.font.color.rgb = RGBColor(0, 0, 0)

    # ── Subject ──────────────────────────────────────
    if letter.subject:
        subj_para = doc.add_paragraph()
        subj_para.alignment = WD_ALIGN_PARAGRAPH.LEFT
        run = subj_para.add_run(letter.subject)
        run.italic = True
        run.font.name = "Roboto"
        run.font.color.rgb = RGBColor(0, 0, 0)

    doc.add_paragraph()

    # ── Body ─────────────────────────────────────────
    # section properties are in EMU; html_to_docx XML needs twips (1 twip = 635 EMU)
    content_width = _emu_to_twips(section.page_width - section.left_margin - section.right_margin)
    if letter.body:
        html_to_docx(letter.body, doc, content_width)

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
    run = sl.add_run(left_text)
    run.font.name = "Roboto"
    run.font.color.rgb = RGBColor(0, 0, 0)

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
        run = sr.add_run(signer_name)
        run.font.name = "Roboto"
        run.font.color.rgb = RGBColor(0, 0, 0)

    # ── Executor ─────────────────────────────────────
    doc.add_paragraph()
    exec_para = doc.add_paragraph()
    exec_text = "Исп.:"
    if letter.creator:
        exec_text += f"\n{letter.creator.full_name}"
        if letter.creator.phone:
            exec_text += f"\n{letter.creator.phone}"
    run = exec_para.add_run(exec_text)
    run.font.name = "Roboto"
    run.font.size = Pt(10)

    doc.save(output_path)
    return output_path
