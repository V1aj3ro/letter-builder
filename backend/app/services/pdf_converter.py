import subprocess
import os


def docx_to_pdf(docx_path: str) -> str:
    output_dir = os.path.dirname(docx_path)
    subprocess.run(
        [
            "libreoffice",
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            output_dir,
            docx_path,
        ],
        check=True,
        timeout=60,
    )
    pdf_path = docx_path.replace(".docx", ".pdf")
    if not os.path.exists(pdf_path):
        raise RuntimeError("PDF generation failed")
    return pdf_path
