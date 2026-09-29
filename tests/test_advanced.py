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

client = TestClient(app)


def test_health_check_returns_database_mode():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "database" in data
    assert "database_mode" in data["database"]


def test_department_classification_and_icd10_prediction():
    # Cardiology test case
    cardio_res = client.post(
        "/extraction/",
        json={
            "report_text": (
                "Patient presents with acute chest pain and palpitations. "
                "ECG shows ST elevation. Prescribed metoprolol 50mg and aspirin 325mg."
            )
        },
    )
    assert cardio_res.status_code == 200
    c_data = cardio_res.json()
    assert c_data["department"] == "Cardiology"
    assert c_data["icd10_code"] in ["I20.9", "I21.9", "I10", "R07.9", "I25.10"]

    # Endocrinology test case
    endo_res = client.post(
        "/extraction/",
        json={
            "report_text": (
                "50-year-old female with elevated HbA1c and fasting blood sugar. "
                "Diagnosed with type 2 diabetes mellitus. Started on metformin 500mg."
            )
        },
    )
    assert endo_res.status_code == 200
    e_data = endo_res.json()
    assert e_data["department"] == "Endocrinology"
    assert e_data["icd10_code"] == "E11.9"

    # Pulmonology test case
    pulmo_res = client.post(
        "/extraction/",
        json={
            "report_text": (
                "Patient complaining of persistent cough, shortness of breath, and wheezing. "
                "Diagnosed with asthma. Albuterol inhaler prescribed."
            )
        },
    )
    assert pulmo_res.status_code == 200
    p_data = pulmo_res.json()
    assert p_data["department"] == "Pulmonology"
    assert p_data["icd10_code"] == "J45.909"


def test_file_upload_extraction_endpoint():
    txt_content = "Patient Jane Doe, 45-year-old female, suffers from gerd and stomach acid. Takes omeprazole."
    response = client.post(
        "/extraction/file",
        files={"file": ("clinical_note.txt", txt_content.encode("utf-8"), "text/plain")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["patient_name"] == "Jane Doe"
    assert "omeprazole" in [m.lower() for m in data["medications"]]
    assert data["department"] == "Gastroenterology"


def test_report_search_filter_analytics_and_delete_flow():
    # Register & login user
    reg = client.post(
        "/auth/register",
        json={"username": "doc_analytics", "email": "analytics@example.com", "password": "pass"},
    )
    assert reg.status_code == 200
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Add 2 reports
    r1 = client.post(
        "/reports/",
        headers=headers,
        json={
            "report_text": "Cardiology report for John. Chest pain and hypertension.",
            "diagnoses": ["hypertension"],
            "symptoms": ["chest pain"],
            "medications": ["lisinopril"],
            "department": "Cardiology",
            "icd10_code": "I10",
            "confidence_score": 0.90,
        },
    )
    assert r1.status_code == 200
    report1_id = r1.json()["id"]

    r2 = client.post(
        "/reports/",
        headers=headers,
        json={
            "report_text": "Endocrinology report for Sarah. Type 2 diabetes.",
            "diagnoses": ["type 2 diabetes"],
            "symptoms": ["fatigue"],
            "medications": ["metformin"],
            "department": "Endocrinology",
            "icd10_code": "E11.9",
            "confidence_score": 0.88,
        },
    )
    assert r2.status_code == 200

    # Search reports by keyword
    search_res = client.get("/reports/?search=Cardiology", headers=headers)
    assert search_res.status_code == 200
    search_data = search_res.json()
    assert len(search_data) == 1
    assert search_data[0]["id"] == report1_id

    # Filter by department
    filter_res = client.get("/reports/?department=Endocrinology", headers=headers)
    assert filter_res.status_code == 200
    assert len(filter_res.json()) == 1
    assert filter_res.json()[0]["department"] == "Endocrinology"

    # Get analytics dashboard stats
    analytics_res = client.get("/reports/analytics", headers=headers)
    assert analytics_res.status_code == 200
    stats = analytics_res.json()
    assert stats["total_reports"] == 2
    assert "Cardiology" in stats["department_counts"]
    assert "Endocrinology" in stats["department_counts"]

    # Delete first report
    del_res = client.delete(f"/reports/{report1_id}", headers=headers)
    assert del_res.status_code == 200

    # Verify report list count is now 1
    remaining_res = client.get("/reports/", headers=headers)
    assert len(remaining_res.json()) == 1
