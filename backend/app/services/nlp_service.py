import hashlib
import re
import random
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import spacy
except Exception:  # pragma: no cover
    spacy = None

try:
    import joblib
except Exception:  # pragma: no cover
    joblib = None

_nlp = None
_diagnosis_model = None
_diagnosis_model_loaded = False
DIAGNOSIS_MODEL_PATH = Path(__file__).resolve().parents[3] / "models" / "diagnosis_classifier.joblib"

DIAGNOSIS_PATTERNS = [
    r"\btype 2 diabetes mellitus\b",
    r"\btype 1 diabetes mellitus\b",
    r"\btype 2 diabetes\b",
    r"\bdiabetes mellitus\b",
    r"\bdiabetes\b",
    r"\bessential hypertension\b",
    r"\bhypertension\b",
    r"\bunstable angina\b",
    r"\bangina\b",
    r"\bmyocardial infarction\b",
    r"\batrial fibrillation\b",
    r"\bheart failure\b",
    r"\barrhythmia\b",
    r"\bgastroesophageal reflux disease\b",
    r"\bgerd\b",
    r"\bastma\b",
    r"\basthma\b",
    r"\bbronchitis\b",
    r"\bpneumonia\b",
    r"\bcopd\b",
    r"\bpulmonary embolism\b",
    r"\bdeep vein thrombosis\b",
    r"\bnephropathy\b",
    r"\bretinopathy\b",
    r"\bneuropathy\b",
    r"\bappendicitis\b",
    r"\bcholecystitis\b",
    r"\bpancreatitis\b",
    r"\bdiverticulitis\b",
    r"\brheumatoid arthritis\b",
    r"\bosteoarthritis\b",
    r"\barthritis\b",
    r"\banemia\b",
    r"\bgout\b",
    r"\bhypothyroidism\b",
    r"\bhyperthyroidism\b",
    r"\bosteoporosis\b",
    r"\bmigraine\b",
    r"\binfection\b",
    r"\bstroke\b",
    r"\bsepsis\b",
    r"\bcancer\b",
    r"\btumor\b",
    r"\bepilepsy\b",
    r"\bgastritis\b",
    r"\bcovid-19\b",
]

SYMPTOM_PATTERNS = [
    r"\bchest pain\b",
    r"\bshortness of breath\b",
    r"\bdyspnea\b",
    r"\bcough\b",
    r"\bfever\b",
    r"\bdizziness\b",
    r"\bheadache\b",
    r"\bfatigue\b",
    r"\bnausea\b",
    r"\bvomiting\b",
    r"\babdominal pain\b",
    r"\bjoint pain\b",
    r"\bpalpitations\b",
    r"\bswelling\b",
    r"\bedema\b",
    r"\brash\b",
    r"\bnumbness\b",
    r"\bback pain\b",
    r"\bknee pain\b",
    r"\bhemoptysis\b",
    r"\bjaundice\b",
    r"\btremor\b",
    r"\banxiety\b",
    r"\bconfusion\b",
]

MEDICATION_PATTERNS = [
    r"\bmetformin\b",
    r"\baspirin\b",
    r"\bparacetamol\b",
    r"\bacetaminophen\b",
    r"\bamoxicillin\b",
    r"\bazithromycin\b",
    r"\binhaler\b",
    r"\balbuterol\b",
    r"\batorvastatin\b",
    r"\bsimvastatin\b",
    r"\bamlodipine\b",
    r"\bhydrochlorothiazide\b",
    r"\blosartan\b",
    r"\bvalsartan\b",
    r"\blevothyroxine\b",
    r"\bgabapentin\b",
    r"\blisinopril\b",
    r"\bsertraline\b",
    r"\blisinopr\b",
    r"\bibuprofen\b",
    r"\bnaproxen\b",
    r"\blomeprazole\b",
    r"\bomeprazole\b",
    r"\bpantoprazole\b",
    r"\bapixaban\b",
    r"\brivaroxaban\b",
    r"\bclopidogrel\b",
    r"\bmetoprolol\b",
    r"\bciprofloxacin\b",
    r"\bamoxil\b",
    r"\binsulin\b",
    r"\bprednisone\b",
    r"\bwarfarin\b",
    r"\bfurosemide\b",
]

DOSAGE_PATTERNS = [
    r"\b\d+\s*(?:mg|g|mcg|ml|units?)\b",
    r"\b(?:once|twice|thrice)\s+(?:daily|a day)\b",
    r"\bevery\s+\d+\s+hours\b",
    r"\b\d+\s*mg\s+twice\s+daily\b",
]

TREATMENT_LAB_PATTERNS = [
    r"\becg\b",
    r"\bekg\b",
    r"\bcardiac enzyme[s]?\b",
    r"\btroponin\b",
    r"\bx-ray\b",
    r"\bchest x-ray\b",
    r"\bmri\b",
    r"\bct scan\b",
    r"\bpet scan\b",
    r"\bblood test[s]?\b",
    r"\bechocardiogram\b",
    r"\bbiopsy\b",
    r"\bphysical therapy\b",
    r"\bendoscopy\b",
    r"\bcolonoscopy\b",
    r"\bblood sugar test\b",
    r"\blipid panel\b",
    r"\bcbc\b",
    r"\bhba1c\b",
    r"\bd-dimer\b",
    r"\burinalysis\b",
    r"\bdialysis\b",
]

ALLERGY_PATTERNS = [
    r"\ballergic to ([a-zA-Z0-9 -]+)",
    r"\ballergy to ([a-zA-Z0-9 -]+)",
    r"\ballergy:\s*([a-zA-Z0-9 -]+)",
    r"\ballergies:\s*([a-zA-Z0-9 -]+)",
]


def compute_text_hash(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", text.strip().lower())
    return hashlib.sha256(cleaned.encode("utf-8")).hexdigest()


def get_model():
    global _nlp
    if _nlp is None and spacy is not None:
        try:
            _nlp = spacy.load("en_core_web_sm")
        except OSError:
            _nlp = False
    return _nlp if _nlp is not None else None


def get_diagnosis_model():
    global _diagnosis_model, _diagnosis_model_loaded
    if not _diagnosis_model_loaded:
        _diagnosis_model_loaded = True
        if joblib is not None and DIAGNOSIS_MODEL_PATH.exists():
            try:
                _diagnosis_model = joblib.load(DIAGNOSIS_MODEL_PATH)
            except Exception:
                _diagnosis_model = None
    return _diagnosis_model


def predict_trained_diagnosis(text: str) -> Optional[str]:
    model = get_diagnosis_model()
    if model is None:
        return None
    try:
        probabilities = model.predict_proba([text])[0]
        best_index = probabilities.argmax()
        if probabilities[best_index] < 0.55:
            return None
        return str(model.classes_[best_index])
    except Exception:
        return None


def _extract_with_patterns(text: str, patterns: List[str]) -> List[str]:
    matches: List[str] = []
    for pattern in patterns:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            value = match.group(0).strip()
            if value and value not in matches:
                matches.append(value)
    return matches


def extract_entities(text: str) -> List[Dict[str, Any]]:
    if not text or not text.strip():
        return []

    entities: List[Dict[str, Any]] = []

    nlp = get_model()
    if nlp is not None and nlp is not False:
        try:
            doc = nlp(text)
            for ent in doc.ents:
                entities.append(
                    {
                        "text": ent.text,
                        "label": ent.label_,
                        "start": ent.start_char,
                        "end": ent.end_char,
                    }
                )
        except Exception:
            pass

    for term in _extract_with_patterns(text, DIAGNOSIS_PATTERNS):
        if not any(e["text"].lower() == term.lower() and e["label"] == "DIAGNOSIS" for e in entities):
            entities.append({"text": term, "label": "DIAGNOSIS"})

    for term in _extract_with_patterns(text, SYMPTOM_PATTERNS):
        if not any(e["text"].lower() == term.lower() and e["label"] == "SYMPTOM" for e in entities):
            entities.append({"text": term, "label": "SYMPTOM"})

    for term in _extract_with_patterns(text, MEDICATION_PATTERNS):
        if not any(e["text"].lower() == term.lower() and e["label"] == "MEDICATION" for e in entities):
            entities.append({"text": term, "label": "MEDICATION"})

    for term in _extract_with_patterns(text, DOSAGE_PATTERNS):
        if not any(e["text"].lower() == term.lower() and e["label"] == "DOSAGE" for e in entities):
            entities.append({"text": term, "label": "DOSAGE"})

    for term in _extract_with_patterns(text, TREATMENT_LAB_PATTERNS):
        if not any(e["text"].lower() == term.lower() and e["label"] == "LAB_TEST" for e in entities):
            entities.append({"text": term, "label": "LAB_TEST"})

    for pattern in ALLERGY_PATTERNS:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            allergy_text = match.group(1) if match.lastindex and match.lastindex >= 1 else match.group(0)
            allergy_text = allergy_text.strip()
            allergy_text = re.sub(r"[\.,;].*$", "", allergy_text).strip()
            if allergy_text and not any(e["text"].lower() == allergy_text.lower() and e["label"] == "ALLERGY" for e in entities):
                entities.append({"text": allergy_text, "label": "ALLERGY"})

    return entities


def classify_department(
    diagnoses: List[str],
    symptoms: List[str],
    medications: List[str],
    lab_tests: List[str],
    text: str,
) -> str:
    t = (text + " " + " ".join(diagnoses) + " " + " ".join(symptoms) + " " + " ".join(medications) + " " + " ".join(lab_tests)).lower()

    cardio_keywords = ["chest pain", "angina", "myocardial infarction", "atrial fibrillation", "hypertension", "cardiology", "ecg", "ekg", "metoprolol", "cardiac", "heart failure", "arrhythmia", "palpitations", "atorvastatin", "clopidogrel", "apixaban"]
    endo_keywords = ["diabetes", "metformin", "insulin", "blood sugar", "hba1c", "endocrinology", "thyroid", "levothyroxine", "glucose"]
    pulmo_keywords = ["asthma", "bronchitis", "pneumonia", "copd", "pulmonary embolism", "cough", "shortness of breath", "inhaler", "pulmonology", "lung"]
    gastro_keywords = ["gerd", "gastroesophageal", "reflux", "omeprazole", "pantoprazole", "abdominal pain", "gastritis", "appendicitis", "cholecystitis", "gastroenterology", "endoscopy", "colonoscopy", "stomach", "nausea"]
    neuro_keywords = ["stroke", "seizure", "epilepsy", "dizziness", "headache", "migraine", "neurology", "numbness", "mri brain", "gabapentin"]
    ortho_keywords = ["fracture", "joint pain", "back pain", "knee pain", "orthopedics", "physical therapy", "x-ray", "bone", "osteoarthritis"]
    onco_keywords = ["cancer", "tumor", "chemotherapy", "radiation", "oncology", "biopsy", "melanoma"]

    scores = {
        "Cardiology": sum(1 for k in cardio_keywords if k in t),
        "Endocrinology": sum(1 for k in endo_keywords if k in t),
        "Pulmonology": sum(1 for k in pulmo_keywords if k in t),
        "Gastroenterology": sum(1 for k in gastro_keywords if k in t),
        "Neurology": sum(1 for k in neuro_keywords if k in t),
        "Orthopedics": sum(1 for k in ortho_keywords if k in t),
        "Oncology": sum(1 for k in onco_keywords if k in t),
    }

    best_dept = max(scores, key=scores.get)
    if scores[best_dept] > 0:
        return best_dept

    return "General Medicine"


def predict_icd10(diagnoses: List[str], department: str) -> str:
    d_str = " ".join(diagnoses).lower()

    if "unstable angina" in d_str or "angina" in d_str:
        return "I20.9"
    if "myocardial infarction" in d_str or "heart attack" in d_str:
        return "I21.9"
    if "atrial fibrillation" in d_str:
        return "I48.91"
    if "essential hypertension" in d_str or "hypertension" in d_str:
        return "I10"
    if "type 2 diabetes" in d_str or "diabetes" in d_str:
        return "E11.9"
    if "asthma" in d_str:
        return "J45.909"
    if "gastroesophageal reflux disease" in d_str or "gerd" in d_str:
        return "K21.9"
    if "stroke" in d_str:
        return "I63.9"
    if "pneumonia" in d_str:
        return "J18.9"
    if "bronchitis" in d_str:
        return "J20.9"
    if "chest pain" in d_str:
        return "R07.9"

    dept_icd_map = {
        "Cardiology": "I25.10",
        "Endocrinology": "E11.9",
        "Pulmonology": "J44.9",
        "Gastroenterology": "K21.9",
        "Neurology": "G44.1",
        "Orthopedics": "M25.50",
        "Oncology": "C80.1",
        "General Medicine": "R50.9",
    }
    return dept_icd_map.get(department, "R50.9")


def determine_triage_and_risk(
    diagnoses: List[str],
    symptoms: List[str],
    allergies: List[str],
    text: str,
) -> tuple[str, str, List[str]]:
    t = (text + " " + " ".join(diagnoses) + " " + " ".join(symptoms)).lower()

    triage_level = "Routine"
    risk_level = "Low"
    flags: List[str] = []

    if any(term in t for term in ["myocardial infarction", "unstable angina", "st elevation", "stroke", "sepsis", "anaphylaxis", "pulmonary embolism"]):
        triage_level = "Emergency"
        risk_level = "Critical"
        flags.append("🚨 CRITICAL ACUTE RISK PROTOCOL")
    elif any(term in t for term in ["chest pain", "shortness of breath", "severe fever", "seizure", "arrhythmia", "atrial fibrillation"]):
        triage_level = "Urgent"
        risk_level = "High"
        flags.append("⚡ URGENT TRIAGE ATTENTION REQUIRED")

    if any(term in t for term in ["angina", "myocardial infarction", "cardiac", "atrial fibrillation"]):
        flags.append("🫀 CARDIAC SURGE WATCH")

    if allergies:
        flags.append(f"⚠️ ALLERGY ALERT: {', '.join(allergies).upper()}")

    if "diabetes" in t or "blood sugar" in t or "hba1c" in t:
        flags.append("🩸 GLUCOSE MONITORING PROTOCOL")

    if "asthma" in t or "copd" in t or "shortness of breath" in t:
        flags.append("🫁 RESPIRATORY SUPPORT PROTOCOL")

    if not flags:
        flags.append("✅ ROUTINE MONITORING")

    return triage_level, risk_level, flags


INVALID_NAME_WORDS = {
    "patient", "patient handover", "handover", "emergency", "hospital", "clinic", "medical",
    "admitted", "discharge", "discharged", "history", "evaluation", "physical", "assessment",
    "doctor", "nurse", "physician", "attending", "specialist", "intake", "triage", "summary",
    "report", "clinical", "note", "was admitted", "admitted for", "presents", "presented",
    "provisional diagnosis", "diagnosis", "provisional", "transferred to", "transferred",
    "history of", "allergic to", "administered", "started on"
}


def parse_patient_metadata(text: str, entities: List[Dict[str, Any]]) -> tuple[Optional[str], Optional[str], Optional[str]]:
    patient_name = None
    age = None
    gender = None

    label_patterns = [
        r"(?:patient\s*name|patient\s*full\s*name|pt\.?\s*name|patient|pt|name|client)\s*[:\-]\s*([A-Za-z][A-Za-z0-9'\.\- ]{1,40})",
        r"\b(?:mr|mrs|ms|miss|dr|sri|smt)\.?\s+([A-Za-z][A-Za-z0-9'\.\- ]{1,40})",
        r"^([A-Za-z][A-Za-z0-9'\.\- ]{1,40})\s*,\s*(?:a|an|the|\d{1,3}\s*y|\d{1,3}\s*year)",
        r"^([A-Za-z][A-Za-z0-9'\.\- ]{1,40})\s+(?:presents|presented|has|complains|reports|came|was\s+admitted)",
        r"^([A-Za-z][A-Za-z0-9'\.\- ]{1,40})\s*\(\s*\d{1,3}\s*[/,\-]?\s*(?:m|f|male|female)",
    ]

    for pattern in label_patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
        if match:
            candidate = match.group(1).strip()
            candidate = re.sub(r"\s+(?:is|was|has|had|presents|presented|complains|reports|admitted|transferred|with|for|a|an)\b.*$", "", candidate, flags=re.IGNORECASE).strip()
            candidate = re.sub(r"[\.,;:].*$", "", candidate).strip()
            if candidate and candidate.lower() not in INVALID_NAME_WORDS and len(candidate) >= 2:
                patient_name = candidate
                break

    if not patient_name and entities:
        for ent in entities:
            if ent.get("label") in ["PERSON", "PER"]:
                val = ent["text"].strip()
                val_clean = re.sub(r"[\.,;:].*$", "", val).strip()
                if val_clean and val_clean.lower() not in INVALID_NAME_WORDS and not re.search(r"\b(?:doctor|dr|nurse|md|attending)\b", val_clean, re.I):
                    patient_name = val_clean
                    break

    age_patterns = [
        r"(\d{1,3})\s*-\s*year\s*-\s*old",
        r"(\d{1,3})\s*years?\s*old",
        r"(\d{1,3})\s*(?:yo|y/o|y\.o\.|yrs|years)",
        r"\baged?\s*[:\-]?\s*(\d{1,3})\b",
        r"\b(\d{1,3})\s*[/,\-]\s*(?:m|f|male|female)\b",
        r"\b(\d{1,3})\s*(?:m|f|male|female)\b",
    ]
    for pattern in age_patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            val = match.group(1)
            if 0 <= int(val) <= 120:
                age = val
                break

    gender_patterns = [
        r"\b(?:sex|gender)\s*[:\-]?\s*(female|male|f|m)\b",
        r"\b\d{1,3}\s*[/,\-]\s*(female|male|f|m)\b",
        r"\b(female|male|woman|man|girl|boy|lady|gentleman)\b",
    ]
    for pattern in gender_patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            val = match.group(1).lower()
            if val in ["female", "f", "woman", "girl", "lady"]:
                gender = "Female"
                break
            elif val in ["male", "m", "man", "boy", "gentleman"]:
                gender = "Male"
                break

    return patient_name, age, gender


def predict_cpt_code(lab_tests: List[str], triage_level: str, department: str) -> tuple[str, str]:
    t_str = " ".join(lab_tests).lower() + " " + triage_level.lower() + " " + department.lower()
    if triage_level == "Emergency":
        return "CPT-99285", "Emergency Department Visit (High Complexity)"
    if "ecg" in t_str or "ekg" in t_str or "cardiac" in t_str:
        return "CPT-93000", "12-Lead Electrocardiogram (ECG) Tracing & Report"
    if "x-ray" in t_str or "chest x-ray" in t_str:
        return "CPT-71045", "Radiologic Examination, Chest; Single View"
    if "troponin" in t_str or "blood test" in t_str or "cbc" in t_str or "hba1c" in t_str:
        return "CPT-80053", "Comprehensive Metabolic Panel & Cardiac Biomarkers"
    if "mri" in t_str or "ct scan" in t_str:
        return "CPT-70450", "Computed Tomography (CT Scan) Diagnostic"
    return "CPT-99214", "Office/Outpatient Visit (Established Patient, 30 Mins)"


def parse_vitals_from_text(text: str) -> Dict[str, Any]:
    vitals: Dict[str, Any] = {
        "bp_sys": "120",
        "bp_dia": "80",
        "temp_f": "98.6",
        "pulse": "72",
        "spo2": "98%",
        "weight_kg": "70",
    }
    bp_match = re.search(r"\b(\d{2,3})\s*/\s*(\d{2,3})\s*(?:mmHg)?\b", text, re.I)
    if bp_match:
        vitals["bp_sys"] = bp_match.group(1)
        vitals["bp_dia"] = bp_match.group(2)

    temp_match = re.search(r"\b(\d{2,3}(?:\.\d)?)\s*°?\s*F\b", text, re.I)
    if temp_match:
        vitals["temp_f"] = temp_match.group(1)

    pulse_match = re.search(r"\b(\d{2,3})\s*(?:bpm|beats|hr\b)", text, re.I)
    if pulse_match:
        vitals["pulse"] = pulse_match.group(1)

    spo2_match = re.search(r"\b(\d{2,3})\s*%\s*(?:spo2|sat)?\b", text, re.I)
    if spo2_match:
        vitals["spo2"] = f"{spo2_match.group(1)}%"

    weight_match = re.search(r"\b(\d{2,3}(?:\.\d)?)\s*kg\b", text, re.I)
    if weight_match:
        vitals["weight_kg"] = weight_match.group(1)

    vitals["bp"] = f"{vitals['bp_sys']}/{vitals['bp_dia']}"
    return vitals


def check_drug_interactions(medications: List[str]) -> List[str]:
    meds_str = " ".join([m.lower() for m in medications])
    alerts: List[str] = []

    if any(m in meds_str for m in ["aspirin", "clopidogrel"]) and any(m in meds_str for m in ["warfarin", "apixaban", "rivaroxaban"]):
        alerts.append("⚠️ HIGH RISK INTERACTION: Dual Anticoagulation/Antiplatelet Therapy (Bleeding Risk)")

    if any(m in meds_str for m in ["metformin"]) and any(m in meds_str for m in ["contrast"]):
        alerts.append("⚠️ CONTRAINDICATION: Metformin with Iodinated Contrast Dye (Lactic Acidosis Risk)")

    return alerts


def calculate_confidence(
    diagnoses: List[str],
    symptoms: List[str],
    medications: List[str],
    patient_name: Optional[str],
    department: str,
) -> float:
    score = 0.70
    if patient_name:
        score += 0.08
    if diagnoses:
        score += 0.08
    if symptoms:
        score += 0.06
    if medications:
        score += 0.05
    if department != "General Medicine":
        score += 0.03

    return round(min(score, 0.98), 2)


def extract_medical_summary(text: str) -> Dict[str, Any]:
    entities = extract_entities(text)
    report_hash = compute_text_hash(text)

    diagnoses = [entity["text"] for entity in entities if entity["label"] == "DIAGNOSIS"]
    symptoms = [entity["text"] for entity in entities if entity["label"] == "SYMPTOM"]
    medications = [entity["text"] for entity in entities if entity["label"] == "MEDICATION"]
    dosages = [entity["text"] for entity in entities if entity["label"] == "DOSAGE"]
    lab_tests = [entity["text"] for entity in entities if entity["label"] == "LAB_TEST"]
    allergies = [entity["text"] for entity in entities if entity["label"] == "ALLERGY"]

    trained_diagnosis = predict_trained_diagnosis(text) if not diagnoses else None
    if trained_diagnosis:
        diagnoses.append(trained_diagnosis)

    patient_name, age, gender = parse_patient_metadata(text, entities)
    vitals = parse_vitals_from_text(text)
    drug_alerts = check_drug_interactions(medications)

    department = classify_department(diagnoses, symptoms, medications, lab_tests, text)
    icd10_code = predict_icd10(diagnoses, department)
    cpt_code, cpt_description = predict_cpt_code(lab_tests, "Emergency" if "severe" in text.lower() else "Routine", department)
    triage_level, risk_level, clinical_flags = determine_triage_and_risk(diagnoses, symptoms, allergies, text)
    clinical_flags.extend(drug_alerts)
    confidence_score = calculate_confidence(diagnoses, symptoms, medications, patient_name, department)

    patient_id = f"PAT-2026-{random.randint(1000, 9999)}"
    room_number = "ICU-02" if triage_level == "Emergency" else ("Room 304-B" if triage_level == "Urgent" else "Outpatient / Ward 1")
    admission_status = "ICU" if triage_level == "Emergency" else ("Admitted" if triage_level == "Urgent" else "Outpatient")

    return {
        "report_hash": report_hash,
        "patient_id": patient_id,
        "patient_name": patient_name,
        "age": age,
        "gender": gender,
        "room_number": room_number,
        "admission_status": admission_status,
        "triage_level": triage_level,
        "attending_physician": "Dr. N. Patel (Attending)",
        "risk_level": risk_level,
        "clinical_flags": clinical_flags,
        "diagnoses": diagnoses,
        "symptoms": symptoms,
        "medications": medications,
        "dosages": dosages,
        "allergies": allergies,
        "lab_tests": lab_tests,
        "raw_entities": entities,
        "department": department,
        "icd10_code": icd10_code,
        "cpt_code": cpt_code,
        "cpt_description": cpt_description,
        "vitals": vitals,
        "confidence_score": confidence_score,
    }