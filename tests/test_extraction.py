import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1] / "backend"))

from app.main import app


client = TestClient(app)


def test_extract_endpoint_returns_structured_results():
    response = client.post(
        "/extraction/",
        json={
            "report_text": (
                "Patient John Doe, 58-year-old male, has diabetes and chest pain. "
                "He was prescribed metformin 500mg and aspirin. Allergic to penicillin."
            )
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["patient_name"] == "John Doe"
    assert "diabetes" in data["diagnoses"]
    assert "chest pain" in data["symptoms"]
    assert "metformin" in data["medications"]
    assert "aspirin" in data["medications"]
    assert "penicillin" in data["allergies"]


def test_extract_does_not_invent_patient_name_for_non_name_notes():
    response = client.post(
        "/extraction/",
        json={
            "report_text": (
                "A 52-year-old male was admitted with differential diagnoses including unstable angina, "
                "myocardial infarction, and gastroesophageal reflux disease. An ECG and cardiac enzyme tests were ordered, "
                "aspirin 325 mg was administered, and the patient was admitted for further evaluation, monitoring, "
                "and cardiology consultation. The provisional diagnoses were unstable angina, essential hypertension, "
                "and type 2 diabetes mellitus."
            )
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["patient_name"] in (None, "") or data["patient_name"] == "—" or "was admitted" not in data["patient_name"].lower()


def test_extract_matches_sample_clinical_note_contents():
    response = client.post(
        "/extraction/",
        json={
            "report_text": (
                "A 52-year-old male was admitted with differential diagnoses including unstable angina, "
                "myocardial infarction, and gastroesophageal reflux disease. An ECG and cardiac enzyme tests were ordered, "
                "aspirin 325 mg was administered, and the patient was admitted for further evaluation, monitoring, "
                "and cardiology consultation. The provisional diagnoses were unstable angina, essential hypertension, "
                "and type 2 diabetes mellitus."
            )
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["age"] == "52"
    assert data["gender"] == "Male"
    assert "unstable angina" in " ".join(data["diagnoses"]).lower()
    assert "myocardial infarction" in " ".join(data["diagnoses"]).lower()
    assert "gastroesophageal reflux disease" in " ".join(data["diagnoses"]).lower()
    assert "essential hypertension" in " ".join(data["diagnoses"]).lower()
    assert "type 2 diabetes mellitus" in " ".join(data["diagnoses"]).lower()
    assert "aspirin" in " ".join(data["medications"]).lower()


def test_extract_handles_name_first_clinical_note_format():
    response = client.post(
        "/extraction/",
        json={
            "report_text": (
                "John Smith, a 52-year-old male, presented to the clinic with complaints of persistent chest pain and "
                "shortness of breath for the past three days. He described the chest pain as a pressure-like sensation "
                "located in the center of the chest, occasionally radiating to the left arm, which worsened with physical activity "
                "and improved with rest. He also reported fatigue and mild dizziness but denied fever, cough, or recent trauma. "
                "His past medical history included hypertension and type 2 diabetes mellitus."
            )
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["patient_name"] == "John Smith"
    assert data["age"] == "52"
    assert data["gender"] == "Male"


def test_extract_handles_single_word_names_and_various_metadata_formats():
    response = client.post(
        "/extraction/",
        json={
            "report_text": (
                "Patient: Kavitha, 45yo female presented with severe headache and fever. "
                "History of hypertension."
            )
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["patient_name"] == "Kavitha"
    assert data["age"] == "45"
    assert data["gender"] == "Female"

    assert "headache" in " ".join(data["symptoms"]).lower()
    assert "fever" in " ".join(data["symptoms"]).lower()
    assert "hypertension" in " ".join(data["diagnoses"]).lower()
