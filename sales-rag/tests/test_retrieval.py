import unittest
from app.retrieval import hybrid_search

class TestRetrieval(unittest.TestCase):
    def test_brightspace_beam_angle_retrieval(self):
        results = hybrid_search(query="What is the beam angle of BrightSpace?", top_k=3)
        self.assertGreater(len(results), 0)
        top_result = results[0]
        self.assertEqual(top_result["product_family"], "BrightSpace")
        self.assertIn("15°, 24°, 36°", top_result["evidence"])

    def test_luxspace_cct_retrieval(self):
        results = hybrid_search(query="What is the CCT of LuxSpace?", top_k=3)
        self.assertGreater(len(results), 0)
        top_result = results[0]
        self.assertEqual(top_result["product_family"], "LuxSpace")
        self.assertIn("2700K", top_result["evidence"])

    def test_ecobright_spotlight_retrieval(self):
        results = hybrid_search(query="EcoBright Spotlight wattage and beam angle", top_k=3)
        self.assertGreater(len(results), 0)
        top_result = results[0]
        self.assertEqual(top_result["product_family"], "EcoBright Spotlight")
        self.assertIn("3W", top_result["evidence"])

    def test_dimming_laserlux_retrieval(self):
        results = hybrid_search(query="Is LaserLux dimmable with DALI or TRIAC?", top_k=3)
        self.assertGreater(len(results), 0)
        top_result = results[0]
        self.assertEqual(top_result["product_family"], "LaserLux")
        self.assertIn("DALI", top_result["evidence"])

if __name__ == "__main__":
    unittest.main()
