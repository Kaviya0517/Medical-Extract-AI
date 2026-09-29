import os
import sys
import uuid
from pathlib import Path

from fastapi.testclient import TestClient

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
os.environ["DATABASE_PATH"] = str(DATA_DIR / f"mediextract_test_{uuid.uuid4().hex}.db")

sys.path.append(str(BASE_DIR / "backend"))

from app.main import app


def test_register_login_and_report_flow():
    client = TestClient(app)

    register_response = client.post(
        "/auth/register",
        json={
            "username": "doctor1",
            "email": "doctor1@example.com",
            "password": "securepass123",
        },
    )
    assert register_response.status_code == 200

    login_response = client.post(
        "/auth/login",
        json={
            "username": "doctor1",
            "password": "securepass123",
        },
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    create_report_response = client.post(
        "/reports/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "report_text": "Patient has diabetes and chest pain.",
            "diagnoses": ["diabetes"],
            "symptoms": ["chest pain"],
            "medications": ["metformin"],
            "allergies": ["penicillin"],
            "department": "General Medicine",
            "icd10_code": "R50.9",
            "confidence_score": 0.86,
        },
    )
    assert create_report_response.status_code == 200

    list_reports_response = client.get(
        "/reports/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert list_reports_response.status_code == 200
    data = list_reports_response.json()
    assert len(data) >= 1
    assert data[0]["report_text"].startswith("Patient has diabetes")
