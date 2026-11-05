import json
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, SimpleTestCase

from apps.analyzer.tests.test_analysis import JOB, RESUME, analysis_data


class ViewTests(SimpleTestCase):
    def test_home_loads_without_a_database(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Resume")
        self.assertNotIn("sessionid", response.cookies)

    def test_unknown_actions_are_rejected(self):
        response = self.client.post("/", {"action": "unknown"})
        self.assertEqual(response.status_code, 400)

    def test_csrf_is_required_for_uploads(self):
        response = Client(enforce_csrf_checks=True).post("/", {"action": "extract"})
        self.assertEqual(response.status_code, 403)

    def test_unsupported_upload_displays_a_useful_error(self):
        response = self.client.post("/", {"action": "extract", "resume": SimpleUploadedFile("cv.txt", b"Hello")})
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, "PDF or DOCX", status_code=400)

    def test_short_input_is_rejected_before_an_api_request(self):
        response = self.client.post("/", {"action": "analyze", "resume_text": "Hello", "job_description": "Developer"})
        self.assertEqual(response.status_code, 400)

    def test_pdf_upload_opens_editable_preview_without_saving(self):
        import pymupdf

        with pymupdf.open() as document:
            document.new_page().insert_text((72, 72), RESUME)
            upload = SimpleUploadedFile("cv.pdf", document.tobytes())
        response = self.client.post("/", {"action": "extract", "resume": upload, "job_description": JOB})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Built Django APIs")
        self.assertContains(response, JOB)

    @patch("apps.analyzer.analysis.genai.Client")
    def test_results_render_and_escape_model_content(self, gemini):
        from types import SimpleNamespace

        from django.test import override_settings

        data = analysis_data()
        data["role"] = "<script>alert(1)</script>"
        gemini.return_value.__enter__.return_value.models.generate_content.return_value = SimpleNamespace(candidates=[SimpleNamespace(finish_reason="STOP")], text=json.dumps(data))
        with override_settings(GEMINI_API_KEY="test-key"):
            response = self.client.post("/", {"action": "analyze", "resume_text": RESUME, "job_description": JOB})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "50%")
        self.assertNotContains(response, "<script>alert(1)</script>")
        self.assertContains(response, "&lt;script&gt;alert(1)&lt;/script&gt;")

    @patch("apps.analyzer.views.analyze_resume", side_effect=ValueError("The analysis service is unavailable. Please try again."))
    def test_provider_failure_keeps_user_inputs(self, analyze):
        response = self.client.post("/", {"action": "analyze", "resume_text": RESUME, "job_description": JOB})
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, RESUME, status_code=400)
        self.assertContains(response, "Please try again", status_code=400)
