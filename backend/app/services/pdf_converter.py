import asyncio
import os


async def docx_to_pdf(docx_path: str) -> str:
    """Convert DOCX to PDF using LibreOffice headless (async, non-blocking)."""
    output_dir = os.path.dirname(docx_path) or "."
    proc = await asyncio.create_subprocess_exec(
        "libreoffice",
        "--headless",
        "--convert-to",
        "pdf",
        "--outdir",
        output_dir,
        docx_path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        err_text = stderr.decode(errors="replace").strip() if stderr else "unknown error"
        raise RuntimeError(f"LibreOffice conversion failed (rc={proc.returncode}): {err_text}")
    pdf_path = docx_path.replace(".docx", ".pdf")
    if not os.path.exists(pdf_path):
        raise RuntimeError("PDF generation failed — output file not found")
    return pdf_path
