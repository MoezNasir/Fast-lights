import unittest
from app.main import query_spec
from app.schemas import QueryRequest

class TestGrounding(unittest.TestCase):
    def test_grounded_answer_brightspace_beam(self):
        req = QueryRequest(question="What is the beam angle of BrightSpace?")
        res = query_spec(req)
        self.assertEqual(res.status, "FOUND")
        self.assertEqual(res.product, "BrightSpace")
        self.assertTrue("15°" in res.natural_response or "15" in res.natural_response)
        self.assertTrue("24°" in res.natural_response or "24" in res.natural_response)
        self.assertTrue("36°" in res.natural_response or "36" in res.natural_response)
        self.assertEqual(res.source.document, "BrightSpace.pdf")

    def test_grounded_answer_eco_downlight_warranty(self):
        req = QueryRequest(question="What is the warranty on Eco-Downlight?")
        res = query_spec(req)
        self.assertEqual(res.status, "FOUND")
        self.assertEqual(res.product, "Eco Downlight")
        self.assertIn("2", res.natural_response.lower())
        self.assertIn("year", res.natural_response.lower())
        self.assertEqual(res.source.document, "Eco-Downlight.pdf")

    def test_grounded_answer_laserlux_dimming(self):
        req = QueryRequest(question="Is LaserLux dimmable?")
        res = query_spec(req)
        self.assertEqual(res.status, "FOUND")
        self.assertTrue("dimmable" in res.natural_response.lower() or "yes" in res.natural_response.lower() or "triac" in res.natural_response.lower())

    def test_grounded_answer_ecobright_wattage(self):
        req = QueryRequest(question="What is the wattage of EcoBright Spotlight?")
        res = query_spec(req)
        self.assertEqual(res.status, "FOUND")
        self.assertIn("3", res.natural_response)

    def test_grounded_answer_brightspace_cutout(self):
        req = QueryRequest(question="What is the cutout dimension for BrightSpace 10W?")
        res = query_spec(req)
        self.assertEqual(res.status, "FOUND")
        self.assertIn("75", res.natural_response)

if __name__ == "__main__":
    unittest.main()
