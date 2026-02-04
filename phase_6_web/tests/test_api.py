from fastapi.testclient import TestClient
import sys
import os
import unittest

# Add project root to path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.append(PROJECT_ROOT)

from phase_6_web.src.main import app

class TestPhase6API(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_root_endpoint(self):
        """Test if the main HTML page loads"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Zomato AI", response.text)

    def test_cities_endpoint(self):
        """Test if cities endpoint returns data"""
        response = self.client.get("/api/v1/cities")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("cities", data)
        self.assertIsInstance(data["cities"], list)

    def test_prices_endpoint(self):
        """Test if prices endpoint returns correct values"""
        response = self.client.get("/api/v1/prices")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("prices", data)
        self.assertIn("Mid-Range", data["prices"])

    # Skipping recommendation test in basic suite to avoid hitting API/DB heavy load in simple verification.
    # The integration test covered the core logic. 
    # This test verifies the API layer wiring.
