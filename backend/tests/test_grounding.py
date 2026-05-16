import unittest

from backend.evaluation import grounding


class GroundingTests(unittest.TestCase):
    def setUp(self):
        self.original_embed_query = grounding.embedding_service.embed_query

    def tearDown(self):
        grounding.embedding_service.embed_query = self.original_embed_query

    def test_assess_retrieval_coverage_passes_for_relevant_docs(self):
        def fake_embed_query(text):
            lowered = text.lower()
            if "quantum" in lowered:
                return [0.95, 0.05]
            return [0.9, 0.1]

        grounding.embedding_service.embed_query = fake_embed_query

        result = grounding.assess_retrieval_coverage(
            "What is quantum entanglement?",
            ["Quantum entanglement is a physical phenomenon in physics."],
        )

        self.assertTrue(result["passed"])
        self.assertGreater(result["score"], 0.0)

    def test_assess_retrieval_coverage_fails_without_docs(self):
        result = grounding.assess_retrieval_coverage("What is recursion?", [])

        self.assertFalse(result["passed"])
        self.assertEqual(result["score"], 0.0)


if __name__ == "__main__":
    unittest.main()