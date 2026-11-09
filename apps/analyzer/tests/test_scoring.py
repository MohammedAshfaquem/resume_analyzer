from unittest import TestCase

from apps.analyzer.utils import calculate_score


class ScoringTests(TestCase):
    def test_required_items_count_twice_and_partial_gets_half_credit(self):
        requirements = [
            {"importance": "required", "status": "supported"},
            {"importance": "required", "status": "partial"},
            {"importance": "preferred", "status": "missing"},
            {"importance": "preferred", "status": "unclear"},
        ]
        self.assertEqual(calculate_score(requirements), 50)

    def test_empty_requirements_do_not_produce_a_perfect_score(self):
        self.assertIsNone(calculate_score([]))

    def test_all_supported_requirements_score_one_hundred(self):
        self.assertEqual(calculate_score([{"importance": "required", "status": "supported"}]), 100)
