import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api.auth import _create_access_token
from app.services.nlp_service import (
    extract_medical_summary,
    predict_cpt_code,
    check_drug_interactions
)

client = TestClient(app)

def get_auth_headers():
    token = _create_access_token("testdoc", role="Doctor", hospital_name="St. Jude Hospital")
    return {"Authorization": f"Bearer {token}"}

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "database" in data

def test_nlp_service_extraction():
    note = "Patient Alex Johnson, 45-year-old male. BP 120/80, Temp 98.6 F. Chief complaint: Severe chest pain for 2 hours. ECG performed. Prescribed Aspirin 325mg and Warfarin 5mg. History of Hypertension."
    result = extract_medical_summary(note)

    assert result["patient_name"] == "Alex Johnson"
    assert "45" in str(result["age"])
    assert result["gender"] in ["Male", "M"]
    assert any("chest pain" in s.lower() for s in result["symptoms"])
    assert any("hypertension" in d.lower() for d in result["diagnoses"])
    assert any("aspirin" in m.lower() for m in result["medications"])
    assert result["icd10_code"] is not None
    assert result["cpt_code"] is not None
    assert result["vitals"]["bp"] == "120/80"

def test_cpt_prediction():
    cpt, desc = predict_cpt_code(["ecg"], "Emergency", "Cardiology")
    assert cpt in ["CPT-93000", "CPT-99285", "CPT-99214", "CPT-80053", "CPT-71045"]

def test_drug_interactions():
    interactions = check_drug_interactions(["Aspirin 325mg", "Warfarin 5mg"])
    assert len(interactions) > 0
    assert any("Bleeding Risk" in item for item in interactions)

def test_auth_workflow():
    reg_payload = {
        "username": "testdoc_suite",
        "email": "testdoc_suite@hospital.org",
        "password": "SecretPassword123!",
        "role": "Doctor",
        "hospital_name": "St. Jude Metro Center"
    }
    reg_res = client.post("/auth/register", json=reg_payload)
    assert reg_res.status_code in [200, 400]

    login_res = client.post("/auth/login", json={"username": "testdoc_suite", "password": "SecretPassword123!"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    assert token is not None

def test_patient_api():
    headers = get_auth_headers()
    payload = {
        "name": "Sarah Connor",
        "age": "34",
        "gender": "Female",
        "phone": "+1-555-0192",
        "email": "sarah@connor.org",
        "past_illnesses": ["Asthma"],
        "allergies": ["Penicillin"]
    }
    res = client.post("/patients/", json=payload, headers=headers)
    assert res.status_code == 200
    p_data = res.json()
    assert p_data["name"] == "Sarah Connor"
    assert "patient_id" in p_data

    get_res = client.get("/patients/", headers=headers)
    assert get_res.status_code == 200
    assert len(get_res.json()) > 0

def test_appointment_api():
    headers = get_auth_headers()
    payload = {
        "patient_id": "PAT-TEST-001",
        "patient_name": "Sarah Connor",
        "doctor_name": "Dr. N. Patel",
        "department": "Cardiology",
        "appointment_date": "2026-09-28",
        "appointment_time": "10:00 AM",
        "notes": "Routine Cardiac Checkup"
    }
    res = client.post("/appointments/", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["token_number"] is not None

def test_lab_api():
    headers = get_auth_headers()
    payload = {
        "patient_id": "PAT-TEST-001",
        "patient_name": "Sarah Connor",
        "test_name": "Comprehensive Metabolic Panel",
        "ordering_doctor": "Dr. N. Patel",
        "department": "Cardiology",
        "notes": "Urgent lab check"
    }
    res = client.post("/lab/orders", json=payload, headers=headers)
    assert res.status_code == 200
    lab_id = res.json()["id"]

    res_update = client.patch(f"/lab/orders/{lab_id}/result", json={
        "result_value": "Glucose 145 mg/dL",
        "normal_range": "70-99 mg/dL",
        "flag": "HIGH",
        "status": "Completed"
    }, headers=headers)
    assert res_update.status_code == 200
    assert res_update.json()["abnormal_flag"] == "HIGH"

def test_fhir_export():
    headers = get_auth_headers()
    res = client.get("/fhir/Patient/PAT-TEST-001", headers=headers)
    assert res.status_code in [200, 404]
