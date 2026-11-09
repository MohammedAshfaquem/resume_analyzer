from io import BytesIO
from unittest import TestCase

import pymupdf
from django.core.files.uploadedfile import SimpleUploadedFile
from docx import Document

from apps.analyzer.utils import extract_resume


class ParsingTests(TestCase):
    def test_pdf_text_is_extracted(self):
        with pymupdf.open() as document:
            page = document.new_page()
            page.insert_text((72, 72), "Python developer building Django APIs.")
            data = document.tobytes()
        upload = SimpleUploadedFile("resume.pdf", data)
        self.assertIn("Python developer building Django APIs.", extract_resume(upload))

    def test_docx_includes_table_content_in_reading_order(self):
        document = Document()
        document.add_paragraph("Python developer")
        document.add_table(rows=1, cols=1).cell(0, 0).text = "Django and PostgreSQL"
        document.add_paragraph("Education: Computer Science")
        stream = BytesIO()
        document.save(stream)
        upload = SimpleUploadedFile("resume.docx", stream.getvalue())
        self.assertEqual(extract_resume(upload), "Python developer\nDjango and PostgreSQL\nEducation: Computer Science")

    def test_invalid_files_are_rejected(self):
        for filename, data in [("resume.exe", b"bad"), ("resume.pdf", b"bad"), ("resume.docx", b"bad"), ("resume.pdf", b"")]:
            with self.subTest(filename=filename, data=data):
                with self.assertRaises(ValueError):
                    extract_resume(SimpleUploadedFile(filename, data))

    def test_oversized_upload_is_rejected_before_parsing(self):
        upload = SimpleUploadedFile("resume.pdf", b"x" * (5 * 1024 * 1024 + 1))
        with self.assertRaisesRegex(ValueError, "5 MB"):
            extract_resume(upload)

    def test_image_only_pdf_explains_that_ocr_is_needed(self):
        with pymupdf.open() as document:
            document.new_page()
            data = document.tobytes()
        with self.assertRaisesRegex(ValueError, "scanned|selectable"):
            extract_resume(SimpleUploadedFile("scan.pdf", data))

    def test_pdf_page_limit_is_enforced(self):
        with pymupdf.open() as document:
            for _ in range(16):
                document.new_page()
            data = document.tobytes()
        with self.assertRaisesRegex(ValueError, "15 pages"):
            extract_resume(SimpleUploadedFile("long.pdf", data))
