import json
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

from django.test import override_settings

from apps.analyzer.analysis import analyze_resume, prepare_result


RESUME = "Built Django APIs with Python and wrote automated tests for a student project."
JOB = "We require Python and Docker. Experience with Django is preferred."


def analysis_data():
    return {
        "role": "Backend developer",
        "summary": "Python experience is demonstrated; Docker is not demonstrated.",
        "requirements": [
            {"requirement": "Python", "job_evidence": "require Python", "importance": "required", "status": "supported", "resume_evidence": "Django APIs with Python", "explanation": "Used Python in a project.", "action": "Explain your contribution."},
            {"requirement": "Docker", "job_evidence": "Docker", "importance": "required", "status": "missing", "resume_evidence": "", "explanation": "No Docker experience is shown.", "action": "If you have used Docker, describe it; otherwise practice containerizing a project."},
        ],
        "improvements": ["Clarify what the APIs did."],
        "rewrites": [{"original": "Built Django APIs with Python", "suggested": "Developed Django APIs using Python for a student project."}],
    }


class AnalysisTests(TestCase):
    def test_score_uses_verified_evidence(self):
        result = prepare_result(analysis_data(), RESUME, JOB)
        self.assertEqual(result["score"], 50)
        self.assertEqual(result["supported_count"], 1)
        self.assertEqual(result["gap_count"], 1)

    def test_fabricated_resume_quote_earns_no_credit(self):
        data = analysis_data()
        data["requirements"][0]["resume_evidence"] = "Ten years building Python applications"
        result = prepare_result(data, RESUME, JOB)
        self.assertEqual(result["score"], 0)
        self.assertEqual(result["requirements"][0]["status"], "unclear")
        self.assertEqual(result["requirements"][0]["resume_evidence"], "")

    def test_fabricated_job_requirements_are_rejected(self):
        data = analysis_data()
        data["requirements"][0]["job_evidence"] = "Must have Kubernetes"
        with self.assertRaises(ValueError):
            prepare_result(data, RESUME, JOB)

    def test_blank_job_quotes_cannot_bypass_evidence_checks(self):
        data = analysis_data()
        data["requirements"][0]["job_evidence"] = "   "
        with self.assertRaises(ValueError):
            prepare_result(data, RESUME, JOB)

    def test_rewrites_without_an_original_source_are_removed(self):
        data = analysis_data()
        data["rewrites"][0]["original"] = "Led a team of twenty engineers"
        self.assertEqual(prepare_result(data, RESUME, JOB)["rewrites"], [])

    def test_duplicate_requirements_cannot_inflate_the_score(self):
        data = analysis_data()
        data["requirements"].append(data["requirements"][0].copy())
        with self.assertRaises(ValueError):
            prepare_result(data, RESUME, JOB)

    @override_settings(GEMINI_API_KEY="")
    def test_missing_api_key_has_an_actionable_error(self):
        with self.assertRaisesRegex(ValueError, "GEMINI_API_KEY"):
            analyze_resume(RESUME, JOB)

    @override_settings(GEMINI_API_KEY="test-key", GEMINI_MODEL="test-model")
    @patch("apps.analyzer.analysis.genai.Client")
    def test_provider_response_runs_through_evidence_checks(self, gemini):
        client = gemini.return_value.__enter__.return_value
        client.models.generate_content.return_value = SimpleNamespace(
            candidates=[SimpleNamespace(finish_reason="STOP")], text=json.dumps(analysis_data())
        )
        self.assertEqual(analyze_resume(RESUME, JOB)["score"], 50)
        arguments = client.models.generate_content.call_args.kwargs
        self.assertEqual(arguments["config"].response_mime_type, "application/json")
        self.assertEqual(json.loads(arguments["contents"])["resume"], RESUME)
        self.assertEqual(arguments["model"], "test-model")

    @override_settings(GEMINI_API_KEY="test-key")
    @patch("apps.analyzer.analysis.genai.Client")
    def test_provider_refusal_is_not_rendered_as_a_valid_report(self, gemini):
        gemini.return_value.__enter__.return_value.models.generate_content.return_value = SimpleNamespace(candidates=[], text=None)
        with self.assertRaisesRegex(ValueError, "complete analysis"):
            analyze_resume(RESUME, JOB)

    @override_settings(GEMINI_API_KEY="test-key")
    @patch("apps.analyzer.analysis.genai.Client")
    def test_truncated_response_cannot_become_a_report(self, gemini):
        gemini.return_value.__enter__.return_value.models.generate_content.return_value = SimpleNamespace(
            candidates=[SimpleNamespace(finish_reason="MAX_TOKENS")], text=json.dumps(analysis_data())
        )
        with self.assertRaisesRegex(ValueError, "complete analysis"):
            analyze_resume(RESUME, JOB)

    @override_settings(GEMINI_API_KEY="test-key")
    @patch("apps.analyzer.analysis.genai.Client")
    def test_malformed_json_has_a_useful_error(self, gemini):
        gemini.return_value.__enter__.return_value.models.generate_content.return_value = SimpleNamespace(
            candidates=[SimpleNamespace(finish_reason="STOP")], text="not json"
        )
        with self.assertRaisesRegex(ValueError, "could not be validated"):
            analyze_resume(RESUME, JOB)

    @override_settings(GEMINI_API_KEY="test-key")
    @patch("apps.analyzer.analysis.genai.Client")
    def test_connection_errors_do_not_expose_provider_details(self, gemini):
        from httpx import ConnectError

        gemini.return_value.__enter__.return_value.models.generate_content.side_effect = ConnectError("private provider details")
        with self.assertRaisesRegex(ValueError, "Gemini is unavailable") as raised:
            analyze_resume(RESUME, JOB)
        self.assertNotIn("private provider details", str(raised.exception))
