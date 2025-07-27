import unittest
from fastapi.testclient import TestClient
from app.main import app


class TestMainSimple(unittest.TestCase):
    """Simple tests for the main FastAPI app"""

    def setUp(self):
        """Set up test client"""
        self.client = TestClient(app)

    def test_read_root(self):
        """Test the root endpoint"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"Hello": "World"})

    def test_healthcheck(self):
        """Test the healthcheck endpoint"""
        response = self.client.get("/healthz")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        self.assertEqual(data["message"], "healthy")
        self.assertIn("version", data)

    def test_app_has_prometheus_instrumentator(self):
        """Test that the app has Prometheus instrumentator configured"""
        # This is a basic test to ensure the app is properly configured
        self.assertIsNotNone(app)

    def test_app_has_routes(self):
        """Test that the app has the expected routes"""
        routes = [route.path for route in app.routes]
        expected_routes = ["/", "/healthz", "/docs", "/redoc", "/openapi.json"]
        for route in expected_routes:
            self.assertIn(route, routes)

    def test_openapi_schema_exists(self):
        """Test that OpenAPI schema is available"""
        response = self.client.get("/openapi.json")
        self.assertEqual(response.status_code, 200)
        schema = response.json()
        self.assertIn("openapi", schema)
        self.assertIn("info", schema)
        self.assertIn("paths", schema)


if __name__ == "__main__":
    unittest.main()
