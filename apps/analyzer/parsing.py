from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

import pymupdf
from docx import Document
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph


MAX_FILE_SIZE = 5 * 1024 * 1024
MAX_RESUME_LENGTH = 40_000


def extract_resume(upload) -> str:
    """Read a bounded upload without storing a copy of the resume."""
    extension = Path(upload.name).suffix.lower()
    if extension not in {".pdf", ".docx"}:
        raise ValueError("Please upload a PDF or DOCX resume.")
    if upload.size > MAX_FILE_SIZE:
        raise ValueError("Your resume must be smaller than 5 MB.")
    data = upload.read(MAX_FILE_SIZE + 1)
    if not data or len(data) > MAX_FILE_SIZE:
        raise ValueError("Upload a non-empty PDF or DOCX smaller than 5 MB.")

    text = extract_pdf(data) if extension == ".pdf" else extract_docx(data)
    text = text.replace("\x00", "").strip()
    if not text:
        raise ValueError("No selectable text was found. If this is a scanned resume, export a text PDF or upload a DOCX; scanned files need OCR.")
    if len(text) > MAX_RESUME_LENGTH:
        raise ValueError("The resume is too long. Please use at most 40,000 characters.")
    return text


def extract_pdf(data: bytes) -> str:
    try:
        document = pymupdf.open(stream=data, filetype="pdf")
    except (RuntimeError, ValueError) as error:
        raise ValueError("This PDF could not be read. Export it again and retry.") from error

    with document:
        if document.needs_pass:
            raise ValueError("Remove the PDF password before uploading.")
        if document.page_count > 15:
            raise ValueError("Please upload a resume with no more than 15 pages.")
        try:
            return "\n".join(page.get_text(sort=True) for page in document)
        except (RuntimeError, ValueError) as error:
            raise ValueError("This PDF could not be read. Export it again and retry.") from error


def extract_docx(data: bytes) -> str:
    try:
        with ZipFile(BytesIO(data)) as archive:
            if sum(item.file_size for item in archive.infolist()) > 20 * 1024 * 1024:
                raise ValueError("The DOCX contents are too large. Export a simpler resume.")
        document = Document(BytesIO(data))
    except ValueError:
        raise
    except Exception as error:
        # DOCX is a ZIP/XML format; parser errors vary by corrupt document.
        raise ValueError("This DOCX could not be read. Save it again as a .docx file.") from error

    lines = []
    for block in document.element.body:
        if block.tag == qn("w:p"):
            lines.append(Paragraph(block, document).text)
        elif block.tag == qn("w:tbl"):
            table = Table(block, document)
            for row in table.rows:
                lines.append(" | ".join(cell.text for cell in row.cells))
    return "\n".join(line.strip() for line in lines if line.strip())
