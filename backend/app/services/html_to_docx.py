"""
Convert Tiptap HTML to python-docx elements.
Supports: p, strong, em, ul, ol, li, table/tr/td/th.
"""
from bs4 import BeautifulSoup, NavigableString, Tag
from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


def _add_run_with_formatting(paragraph, text: str, bold: bool = False, italic: bool = False):
    run = paragraph.add_run(text)
    run.bold = bold
    run.italic = italic
    return run


def _process_inline(element, paragraph, bold=False, italic=False):
    """Recursively process inline elements into a paragraph."""
    if isinstance(element, NavigableString):
        text = str(element)
        if text:
            _add_run_with_formatting(paragraph, text, bold=bold, italic=italic)
    elif isinstance(element, Tag):
        is_bold = bold or element.name in ("strong", "b")
        is_italic = italic or element.name in ("em", "i")
        for child in element.children:
            _process_inline(child, paragraph, bold=is_bold, italic=is_italic)


def _clear_borders(obj_tbl_or_cell, is_cell: bool = False):
    """Remove all borders from a table or cell XML element."""
    tc_or_tbl = obj_tbl_or_cell._tc if is_cell else obj_tbl_or_cell._tbl
    pr_tag = "w:tcPr" if is_cell else "w:tblPr"
    border_tag = "w:tcBorders" if is_cell else "w:tblBorders"

    pPr = tc_or_tbl.find(qn(pr_tag))
    if pPr is None:
        pPr = OxmlElement(pr_tag)
        tc_or_tbl.insert(0, pPr)

    borders = OxmlElement(border_tag)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        tag = OxmlElement(f"w:{edge}")
        tag.set(qn("w:val"), "none")
        tag.set(qn("w:sz"), "0")
        tag.set(qn("w:color"), "auto")
        borders.append(tag)
    pPr.append(borders)


def _process_table(tag: Tag, document: Document):
    rows = tag.find_all("tr")
    if not rows:
        return

    max_cols = max(len(r.find_all(["td", "th"])) for r in rows)
    if max_cols == 0:
        return

    table = document.add_table(rows=len(rows), cols=max_cols)
    _clear_borders(table)

    for i, row_tag in enumerate(rows):
        cells = row_tag.find_all(["td", "th"])
        for j, cell_tag in enumerate(cells):
            if j >= max_cols:
                break
            cell = table.cell(i, j)
            cell.text = ""
            _clear_borders(cell, is_cell=True)
            para = cell.paragraphs[0]
            is_header = cell_tag.name == "th"
            for child in cell_tag.children:
                _process_inline(child, para, bold=is_header)


def html_to_docx(html: str, document: Document):
    """Parse HTML and append content to the document."""
    if not html:
        return

    soup = BeautifulSoup(html, "html.parser")

    def _process_block(element):
        if isinstance(element, NavigableString):
            text = str(element).strip()
            if text:
                p = document.add_paragraph()
                _add_run_with_formatting(p, text)
            return

        name = element.name if isinstance(element, Tag) else None
        if name is None:
            return

        if name == "p":
            p = document.add_paragraph()
            for child in element.children:
                _process_inline(child, p)

        elif name in ("ul", "ol"):
            style = "List Bullet" if name == "ul" else "List Number"
            for li in element.find_all("li", recursive=False):
                p = document.add_paragraph(style=style)
                for child in li.children:
                    _process_inline(child, p)

        elif name == "table":
            _process_table(element, document)

        elif name in ("div", "section", "article"):
            for child in element.children:
                _process_block(child)

        elif name in ("h1", "h2", "h3", "h4", "h5", "h6"):
            level = int(name[1])
            p = document.add_paragraph()
            for child in element.children:
                _process_inline(child, p, bold=True)

        elif name == "br":
            document.add_paragraph()

        else:
            # Treat unknown block elements as paragraphs
            p = document.add_paragraph()
            for child in element.children:
                _process_inline(child, p)

    # Top-level elements
    for child in soup.children:
        _process_block(child)
