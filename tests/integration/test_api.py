"""Integration tests for the Food Defect AOI REST API."""

import unittest
from pathlib import Path

from fastapi.testclient import TestClient
from src.api.main import app

BASE_DIR = Path(__file__).resolve().parents[2]


class TestInspectionAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(app)
        cls.samples_dir = BASE_DIR / "data" / "samples"

    def test_health_check(self) -> None:
        response = self.client.get("/api/v1/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertTrue(data["model_loaded"])

    def test_inspect_invalid_mimetype(self) -> None:
        response = self.client.post(
            "/api/v1/inspect",
            files={"file": ("test.txt", b"plain text content", "text/plain")},
        )
        self.assertEqual(response.status_code, 415)

    def test_inspect_dataset_defective_fruit(self) -> None:
        sample_path = self.samples_dir / "dataset_defective_fruit.jpg"
        with open(sample_path, "rb") as f:
            response = self.client.post(
                "/api/v1/inspect",
                files={"file": ("dataset_defective_fruit.jpg", f, "image/jpeg")},
            )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("inspection_id", data)
        self.assertIn(
            data["grade"], ["PASS_GRADE_A", "PASS_GRADE_B", "REJECT", "NO_OBJECT"]
        )
        self.assertGreater(data["timing"]["total_ms"], 0.0)
        self.assertGreaterEqual(len(data["defects"]), 1)

    def test_inspect_dataset_healthy_fruit(self) -> None:
        sample_path = self.samples_dir / "dataset_healthy_fruit.jpg"
        with open(sample_path, "rb") as f:
            response = self.client.post(
                "/api/v1/inspect",
                files={"file": ("dataset_healthy_fruit.jpg", f, "image/jpeg")},
            )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("inspection_id", data)
        self.assertIn(
            data["grade"], ["PASS_GRADE_A", "PASS_GRADE_B", "REJECT", "NO_OBJECT"]
        )
        self.assertGreater(data["timing"]["total_ms"], 0.0)

    def test_inspect_int8_precision(self) -> None:
        sample_path = self.samples_dir / "dataset_defective_fruit.jpg"
        with open(sample_path, "rb") as f:
            response = self.client.post(
                "/api/v1/inspect?precision=int8",
                files={"file": ("dataset_defective_fruit.jpg", f, "image/jpeg")},
            )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("inspection_id", data)
        self.assertGreater(data["timing"]["total_ms"], 0.0)


if __name__ == "__main__":
    unittest.main()
