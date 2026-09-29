import json
import os
import random
import sqlite3
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"

if os.getenv("PYTEST_CURRENT_TEST"):
    DB_PATH = Path(os.getenv("DATABASE_PATH", DATA_DIR / f"mediextract_test_{os.getpid()}.db"))
else:
    DB_PATH = Path(os.getenv("DATABASE_PATH", DATA_DIR / "mediextract.db"))


def _connect_sqlite():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            email TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'Doctor',
            hospital_name TEXT DEFAULT 'General Medical Center',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    try:
        conn.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'Doctor'")
    except sqlite3.OperationalError:
        pass
    try:
        conn.execute("ALTER TABLE users ADD COLUMN hospital_name TEXT DEFAULT 'General Medical Center'")
    except sqlite3.OperationalError:
        pass
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS reports (
            id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            report_hash TEXT,
            patient_id TEXT,
            patient_name TEXT,
            age TEXT,
            gender TEXT,
            room_number TEXT,
            admission_status TEXT,
            triage_level TEXT,
            attending_physician TEXT,
            risk_level TEXT,
            clinical_flags TEXT,
            report_text TEXT NOT NULL,
            diagnoses TEXT,
            symptoms TEXT,
            medications TEXT,
            dosages TEXT,
            allergies TEXT,
            lab_tests TEXT,
            department TEXT,
            icd10_code TEXT,
            confidence_score REAL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    for col, col_type in [
        ("report_hash", "TEXT"),
        ("patient_id", "TEXT"),
        ("patient_name", "TEXT"),
        ("age", "TEXT"),
        ("gender", "TEXT"),
        ("room_number", "TEXT"),
        ("admission_status", "TEXT"),
        ("triage_level", "TEXT"),
        ("attending_physician", "TEXT"),
        ("risk_level", "TEXT"),
        ("clinical_flags", "TEXT"),
        ("diagnoses", "TEXT"),
        ("symptoms", "TEXT"),
        ("medications", "TEXT"),
        ("dosages", "TEXT"),
        ("allergies", "TEXT"),
        ("lab_tests", "TEXT"),
        ("department", "TEXT"),
        ("icd10_code", "TEXT"),
        ("confidence_score", "REAL"),
    ]:
        try:
            conn.execute(f"ALTER TABLE reports ADD COLUMN {col} {col_type}")
        except sqlite3.OperationalError:
            pass
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS activity_logs (
            id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            action TEXT NOT NULL,
            details TEXT NOT NULL,
            timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS patients (
            id TEXT PRIMARY KEY,
            patient_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            age TEXT,
            gender TEXT,
            phone TEXT,
            email TEXT,
            address TEXT,
            emergency_contact TEXT,
            insurance_provider TEXT,
            policy_number TEXT,
            past_illnesses TEXT,
            surgeries TEXT,
            allergies TEXT,
            family_history TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS appointments (
            id TEXT PRIMARY KEY,
            patient_id TEXT NOT NULL,
            patient_name TEXT NOT NULL,
            doctor_name TEXT NOT NULL,
            department TEXT NOT NULL,
            appointment_date TEXT NOT NULL,
            appointment_time TEXT NOT NULL,
            appointment_type TEXT DEFAULT 'Scheduled',
            token_number INTEGER,
            notes TEXT,
            status TEXT DEFAULT 'Booked',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS lab_orders (
            id TEXT PRIMARY KEY,
            patient_id TEXT NOT NULL,
            patient_name TEXT NOT NULL,
            test_name TEXT NOT NULL,
            ordering_doctor TEXT NOT NULL,
            department TEXT NOT NULL,
            notes TEXT,
            status TEXT DEFAULT 'Ordered',
            result_value TEXT,
            reference_range TEXT,
            abnormal_flag TEXT,
            completed_at TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS prescriptions (
            id TEXT PRIMARY KEY,
            patient_id TEXT NOT NULL,
            patient_name TEXT NOT NULL,
            doctor_name TEXT NOT NULL,
            medication_name TEXT NOT NULL,
            dosage TEXT NOT NULL,
            frequency TEXT NOT NULL,
            duration TEXT NOT NULL,
            special_instructions TEXT,
            dispensed INTEGER DEFAULT 0,
            dispensed_at TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS invoices (
            id TEXT PRIMARY KEY,
            patient_id TEXT NOT NULL,
            patient_name TEXT NOT NULL,
            consultation_fee REAL DEFAULT 0,
            lab_fee REAL DEFAULT 0,
            pharmacy_fee REAL DEFAULT 0,
            room_charges REAL DEFAULT 0,
            total_amount REAL DEFAULT 0,
            payment_status TEXT DEFAULT 'Pending',
            insurance_claim_amount REAL DEFAULT 0,
            insurance_status TEXT DEFAULT 'Not Submitted',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS staff (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            department TEXT NOT NULL,
            shift TEXT DEFAULT 'Morning',
            phone TEXT,
            email TEXT,
            status TEXT DEFAULT 'Active',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS consumables (
            id TEXT PRIMARY KEY,
            item_name TEXT NOT NULL,
            category TEXT NOT NULL,
            quantity INTEGER DEFAULT 0,
            reorder_level INTEGER DEFAULT 20,
            unit_cost REAL DEFAULT 0,
            vendor_name TEXT,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    return conn


if settings.MONGODB_URL:
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
else:
    client = None
    db = None


def get_database():
    return db


def get_sqlite_user(username: str):
    clean_username = username.strip()
    conn = _connect_sqlite()
    row = conn.execute(
        "SELECT username, email, password_hash, role, hospital_name FROM users WHERE LOWER(username) = LOWER(?)",
        (clean_username,),
    ).fetchone()
    conn.close()
    if row is None:
        return None
    return {
        "username": row[0],
        "email": row[1],
        "password": row[2],
        "role": row[3] or "Doctor",
        "hospital_name": row[4] or "General Medical Center",
    }


def save_sqlite_user(username: str, email: str, password_hash: str, role: str = "Doctor", hospital_name: str = "General Medical Center"):
    conn = _connect_sqlite()
    conn.execute(
        "INSERT OR REPLACE INTO users (username, email, password_hash, role, hospital_name) VALUES (?, ?, ?, ?, ?)",
        (username, email, password_hash, role, hospital_name),
    )
    conn.commit()
    conn.close()


def save_sqlite_report(report: dict):
    conn = _connect_sqlite()
    conn.execute(
        """
        INSERT OR REPLACE INTO reports (
            id, username, report_hash, patient_id, patient_name, age, gender, room_number, admission_status,
            triage_level, attending_physician, risk_level, clinical_flags, report_text,
            diagnoses, symptoms, medications, dosages, allergies, lab_tests,
            department, icd10_code, confidence_score
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            report["id"],
            report["username"],
            report.get("report_hash"),
            report.get("patient_id", "PAT-2026-1001"),
            report.get("patient_name"),
            report.get("age"),
            report.get("gender"),
            report.get("room_number", "Ward 1"),
            report.get("admission_status", "Admitted"),
            report.get("triage_level", "Routine"),
            report.get("attending_physician", "Dr. N. Patel"),
            report.get("risk_level", "Low"),
            json.dumps(report.get("clinical_flags", [])),
            report["report_text"],
            json.dumps(report.get("diagnoses", [])),
            json.dumps(report.get("symptoms", [])),
            json.dumps(report.get("medications", [])),
            json.dumps(report.get("dosages", [])),
            json.dumps(report.get("allergies", [])),
            json.dumps(report.get("lab_tests", [])),
            report.get("department", "General Medicine"),
            report.get("icd10_code", "R50.9"),
            report.get("confidence_score", 0.85),
        ),
    )
    conn.commit()
    conn.close()


def list_sqlite_reports(username: str):
    conn = _connect_sqlite()
    rows = conn.execute(
        """
        SELECT id, username, report_hash, patient_id, patient_name, age, gender, room_number, admission_status,
               triage_level, attending_physician, risk_level, clinical_flags, report_text,
               diagnoses, symptoms, medications, dosages, allergies, lab_tests,
               department, icd10_code, confidence_score
        FROM reports WHERE username = ? ORDER BY created_at DESC
        """,
        (username,),
    ).fetchall()
    conn.close()

    result = []
    for row in rows:
        result.append(
            {
                "id": row[0],
                "username": row[1],
                "report_hash": row[2],
                "patient_id": row[3] or "PAT-2026-1001",
                "patient_name": row[4],
                "age": row[5],
                "gender": row[6],
                "room_number": row[7] or "Ward 1",
                "admission_status": row[8] or "Admitted",
                "triage_level": row[9] or "Routine",
                "attending_physician": row[10] or "Dr. N. Patel",
                "risk_level": row[11] or "Low",
                "clinical_flags": json.loads(row[12] or "[]"),
                "report_text": row[13],
                "diagnoses": json.loads(row[14] or "[]"),
                "symptoms": json.loads(row[15] or "[]"),
                "medications": json.loads(row[16] or "[]"),
                "dosages": json.loads(row[17] or "[]"),
                "allergies": json.loads(row[18] or "[]"),
                "lab_tests": json.loads(row[19] or "[]"),
                "department": row[20] or "General Medicine",
                "icd10_code": row[21] or "R50.9",
                "confidence_score": row[22] or 0.85,
            }
        )
    return result


def delete_sqlite_report(report_id: str, username: str) -> bool:
    conn = _connect_sqlite()
    cursor = conn.execute("DELETE FROM reports WHERE id = ? AND username = ?", (report_id, username))
    conn.commit()
    deleted_rows = cursor.rowcount
    conn.close()
    return deleted_rows > 0


def save_sqlite_activity_log(username: str, action: str, details: str):
    conn = _connect_sqlite()
    conn.execute(
        "INSERT INTO activity_logs (id, username, action, details, timestamp) VALUES (?, ?, ?, ?, ?)",
        (str(uuid4()), username, action, details, datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    conn.close()


def list_sqlite_activity_logs(username: str):
    conn = _connect_sqlite()
    rows = conn.execute(
        "SELECT id, username, action, details, timestamp FROM activity_logs WHERE username = ? ORDER BY timestamp DESC LIMIT 50",
        (username,),
    ).fetchall()
    conn.close()

    return [
        {
            "id": r[0],
            "username": r[1],
            "action": r[2],
            "details": r[3],
            "timestamp": r[4],
        }
        for r in rows
    ]


# --- Async MongoDB Atlas API with SQLite fallback ---

async def check_db_status() -> Dict[str, Any]:
    if db is not None and client is not None:
        try:
            await client.admin.command("ping")
            return {
                "mongodb_configured": True,
                "mongodb_connected": True,
                "database_mode": "MongoDB Atlas",
            }
        except Exception:
            return {
                "mongodb_configured": True,
                "mongodb_connected": False,
                "database_mode": "SQLite Fallback (MongoDB Connection Error)",
            }
    return {
        "mongodb_configured": False,
        "mongodb_connected": False,
        "database_mode": "SQLite Local",
    }


async def get_user_db(username: str) -> Optional[Dict[str, Any]]:
    clean_username = username.strip()
    if db is not None:
        try:
            doc = await db.users.find_one({"username": {"$regex": f"^{clean_username}$", "$options": "i"}})
            if doc:
                return {
                    "username": doc["username"],
                    "email": doc.get("email", ""),
                    "password": doc.get("password_hash") or doc.get("password", ""),
                    "role": doc.get("role", "Doctor"),
                    "hospital_name": doc.get("hospital_name", "General Medical Center"),
                }
        except Exception:
            pass
    return get_sqlite_user(clean_username)


async def save_user_db(username: str, email: str, password_hash: str, role: str = "Doctor", hospital_name: str = "General Medical Center") -> None:
    save_sqlite_user(username, email, password_hash, role, hospital_name)
    if db is not None:
        try:
            await db.users.update_one(
                {"username": username},
                {"$set": {
                    "username": username,
                    "email": email,
                    "password_hash": password_hash,
                    "role": role,
                    "hospital_name": hospital_name,
                }},
                upsert=True,
            )
        except Exception:
            pass


async def update_user_hospital_name_db(username: str, hospital_name: str) -> bool:
    conn = _connect_sqlite()
    conn.execute(
        "UPDATE users SET hospital_name = ? WHERE username = ?",
        (hospital_name, username),
    )
    conn.commit()
    conn.close()

    if db is not None:
        try:
            await db.users.update_one(
                {"username": username},
                {"$set": {"hospital_name": hospital_name}},
            )
        except Exception:
            pass
    return True


async def save_report_db(report: dict) -> dict:
    save_sqlite_report(report)
    if db is not None:
        try:
            await db.reports.update_one(
                {"id": report["id"]},
                {"$set": report},
                upsert=True,
            )
        except Exception:
            pass
    return report


async def check_duplicate_report_db(username: str, report_hash: str) -> Optional[dict]:
    if not report_hash:
        return None

    if db is not None:
        try:
            doc = await db.reports.find_one({"username": username, "report_hash": report_hash})
            if doc:
                return {"id": str(doc.get("id") or doc.get("_id"))}
        except Exception:
            pass

    for r in list_sqlite_reports(username):
        if r.get("report_hash") == report_hash:
            return {"id": r["id"]}

    return None


async def list_reports_db(
    username: str,
    search: Optional[str] = None,
    department: Optional[str] = None,
    triage_level: Optional[str] = None,
    admission_status: Optional[str] = None,
) -> List[dict]:
    reports: List[dict] = []
    if db is not None:
        try:
            query: Dict[str, Any] = {"username": username}
            if department:
                query["department"] = department
            if triage_level:
                query["triage_level"] = triage_level
            if admission_status:
                query["admission_status"] = admission_status

            cursor = db.reports.find(query).sort("_id", -1)
            docs = await cursor.to_list(length=500)
            for item in docs:
                rep = {
                    "id": str(item.get("id") or item.get("_id")),
                    "username": item.get("username", username),
                    "report_hash": item.get("report_hash"),
                    "patient_id": item.get("patient_id", "PAT-2026-1001"),
                    "patient_name": item.get("patient_name"),
                    "age": item.get("age"),
                    "gender": item.get("gender"),
                    "room_number": item.get("room_number", "Ward 1"),
                    "admission_status": item.get("admission_status", "Admitted"),
                    "triage_level": item.get("triage_level", "Routine"),
                    "attending_physician": item.get("attending_physician", "Dr. N. Patel"),
                    "risk_level": item.get("risk_level", "Low"),
                    "clinical_flags": item.get("clinical_flags", []),
                    "report_text": item.get("report_text", ""),
                    "diagnoses": item.get("diagnoses", []),
                    "symptoms": item.get("symptoms", []),
                    "medications": item.get("medications", []),
                    "dosages": item.get("dosages", []),
                    "allergies": item.get("allergies", []),
                    "lab_tests": item.get("lab_tests", []),
                    "department": item.get("department", "General Medicine"),
                    "icd10_code": item.get("icd10_code", "R50.9"),
                    "confidence_score": item.get("confidence_score", 0.85),
                }
                reports.append(rep)
        except Exception:
            reports = []

    if not reports:
        reports = list_sqlite_reports(username)

    filtered = []
    for r in reports:
        if department and r.get("department", "").lower() != department.lower():
            continue
        if triage_level and r.get("triage_level", "").lower() != triage_level.lower():
            continue
        if admission_status and r.get("admission_status", "").lower() != admission_status.lower():
            continue
        if search:
            term = search.lower()
            full_text = (
                f"{r.get('patient_id', '')} {r.get('patient_name', '')} {r.get('room_number', '')} "
                f"{r.get('report_text', '')} {' '.join(r.get('diagnoses', []))} "
                f"{' '.join(r.get('symptoms', []))} {' '.join(r.get('medications', []))} "
                f"{r.get('department', '')} {r.get('icd10_code', '')}"
            ).lower()
            if term not in full_text:
                continue
        filtered.append(r)

    return filtered


async def get_report_db(report_id: str, username: str) -> Optional[dict]:
    if db is not None:
        try:
            doc = await db.reports.find_one({"id": report_id, "username": username})
            if doc:
                return {
                    "id": str(doc.get("id") or doc.get("_id")),
                    "username": doc.get("username", username),
                    "report_hash": doc.get("report_hash"),
                    "patient_id": doc.get("patient_id", "PAT-2026-1001"),
                    "patient_name": doc.get("patient_name"),
                    "age": doc.get("age"),
                    "gender": doc.get("gender"),
                    "room_number": doc.get("room_number", "Ward 1"),
                    "admission_status": doc.get("admission_status", "Admitted"),
                    "triage_level": doc.get("triage_level", "Routine"),
                    "attending_physician": doc.get("attending_physician", "Dr. N. Patel"),
                    "risk_level": doc.get("risk_level", "Low"),
                    "clinical_flags": doc.get("clinical_flags", []),
                    "report_text": doc.get("report_text", ""),
                    "diagnoses": doc.get("diagnoses", []),
                    "symptoms": doc.get("symptoms", []),
                    "medications": doc.get("medications", []),
                    "dosages": doc.get("dosages", []),
                    "allergies": doc.get("allergies", []),
                    "lab_tests": doc.get("lab_tests", []),
                    "department": doc.get("department", "General Medicine"),
                    "icd10_code": doc.get("icd10_code", "R50.9"),
                    "confidence_score": doc.get("confidence_score", 0.85),
                }
        except Exception:
            pass

    for r in list_sqlite_reports(username):
        if r["id"] == report_id:
            return r
    return None


async def delete_report_db(report_id: str, username: str) -> bool:
    mongo_deleted = False
    if db is not None:
        try:
            res = await db.reports.delete_one({"id": report_id, "username": username})
            mongo_deleted = res.deleted_count > 0
        except Exception:
            pass

    sqlite_deleted = delete_sqlite_report(report_id, username)
    return mongo_deleted or sqlite_deleted


async def save_activity_log_db(username: str, action: str, details: str):
    save_sqlite_activity_log(username, action, details)
    if db is not None:
        try:
            await db.activity_logs.insert_one({
                "id": str(uuid4()),
                "username": username,
                "action": action,
                "details": details,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
        except Exception:
            pass


async def list_activity_logs_db(username: str) -> List[dict]:
    logs: List[dict] = []
    if db is not None:
        try:
            cursor = db.activity_logs.find({"username": username}).sort("_id", -1).limit(50)
            docs = await cursor.to_list(length=50)
            for item in docs:
                logs.append({
                    "id": str(item.get("id") or item.get("_id")),
                    "username": item.get("username", username),
                    "action": item.get("action", "ACTION"),
                    "details": item.get("details", ""),
                    "timestamp": item.get("timestamp", ""),
                })
        except Exception:
            logs = []

    if not logs:
        logs = list_sqlite_activity_logs(username)

    return logs


async def get_analytics_db(username: str) -> dict:
    reports = await list_reports_db(username)

    total_reports = len(reports)
    if total_reports == 0:
        return {
            "total_reports": 0,
            "active_admitted": 0,
            "icu_patients": 0,
            "emergency_cases": 0,
            "critical_alerts_count": 0,
            "department_counts": {},
            "triage_counts": {},
            "risk_counts": {},
            "top_diagnoses": [],
            "top_symptoms": [],
            "top_medications": [],
            "avg_confidence": 0.0,
        }

    departments = [r.get("department") or "General Medicine" for r in reports]
    dept_counts = dict(Counter(departments))

    triages = [r.get("triage_level") or "Routine" for r in reports]
    triage_counts = dict(Counter(triages))

    risks = [r.get("risk_level") or "Low" for r in reports]
    risk_counts = dict(Counter(risks))

    active_admitted = sum(1 for r in reports if r.get("admission_status") in ["Admitted", "ICU"])
    icu_patients = sum(1 for r in reports if r.get("admission_status") == "ICU")
    emergency_cases = sum(1 for r in reports if r.get("triage_level") == "Emergency")
    critical_alerts_count = sum(1 for r in reports if r.get("risk_level") in ["Critical", "High"])

    diagnoses_list = [d for r in reports for d in r.get("diagnoses", []) if d]
    top_diagnoses = [{"name": k, "count": v} for k, v in Counter(diagnoses_list).most_common(5)]

    symptoms_list = [s for r in reports for s in r.get("symptoms", []) if s]
    top_symptoms = [{"name": k, "count": v} for k, v in Counter(symptoms_list).most_common(5)]

    meds_list = [m for r in reports for m in r.get("medications", []) if m]
    top_medications = [{"name": k, "count": v} for k, v in Counter(meds_list).most_common(5)]

    scores = [r.get("confidence_score") or 0.85 for r in reports]
    avg_confidence = round(sum(scores) / len(scores), 3)

    return {
        "total_reports": total_reports,
        "active_admitted": active_admitted,
        "icu_patients": icu_patients,
        "emergency_cases": emergency_cases,
        "critical_alerts_count": critical_alerts_count,
        "department_counts": dept_counts,
        "triage_counts": triage_counts,
        "risk_counts": risk_counts,
        "top_diagnoses": top_diagnoses,
        "top_symptoms": top_symptoms,
        "top_medications": top_medications,
        "avg_confidence": avg_confidence,
    }


# --- Password Reset ---
async def reset_password_db(username: str, new_password_hash: str) -> bool:
    conn = _connect_sqlite()
    cursor = conn.execute("UPDATE users SET password_hash = ? WHERE LOWER(username) = LOWER(?)", (new_password_hash, username.strip()))
    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()

    if db is not None:
        try:
            await db.users.update_one({"username": {"$regex": f"^{username.strip()}$", "$options": "i"}}, {"$set": {"password_hash": new_password_hash}})
            updated = True
        except Exception:
            pass

    return updated


# --- Patient CRUD ---
async def save_patient_db(patient_data: dict) -> dict:
    patient_id = patient_data.get("patient_id") or f"PAT-2026-{random.randint(1000, 9999)}"
    record = {
        "id": str(uuid4()),
        "patient_id": patient_id,
        "name": patient_data["name"],
        "age": patient_data.get("age", "30"),
        "gender": patient_data.get("gender", "Female"),
        "phone": patient_data.get("phone", ""),
        "email": patient_data.get("email", ""),
        "address": patient_data.get("address", ""),
        "emergency_contact": patient_data.get("emergency_contact", ""),
        "insurance_provider": patient_data.get("insurance_provider", "Blue Cross"),
        "policy_number": patient_data.get("policy_number", "POL-89410"),
        "past_illnesses": patient_data.get("past_illnesses", []),
        "surgeries": patient_data.get("surgeries", []),
        "allergies": patient_data.get("allergies", []),
        "family_history": patient_data.get("family_history", []),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    conn = _connect_sqlite()
    conn.execute(
        """
        INSERT OR REPLACE INTO patients (
            id, patient_id, name, age, gender, phone, email, address, emergency_contact,
            insurance_provider, policy_number, past_illnesses, surgeries, allergies, family_history, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            record["id"], record["patient_id"], record["name"], record["age"], record["gender"],
            record["phone"], record["email"], record["address"], record["emergency_contact"],
            record["insurance_provider"], record["policy_number"],
            json.dumps(record["past_illnesses"]), json.dumps(record["surgeries"]),
            json.dumps(record["allergies"]), json.dumps(record["family_history"]),
            record["created_at"],
        ),
    )
    conn.commit()
    conn.close()

    if db is not None:
        try:
            await db.patients.update_one({"patient_id": record["patient_id"]}, {"$set": record}, upsert=True)
        except Exception:
            pass

    return record


async def list_patients_db(search_term: Optional[str] = None) -> List[dict]:
    conn = _connect_sqlite()
    if search_term:
        term = f"%{search_term.strip()}%"
        rows = conn.execute(
            "SELECT id, patient_id, name, age, gender, phone, email, address, emergency_contact, insurance_provider, policy_number, past_illnesses, surgeries, allergies, family_history, created_at FROM patients WHERE patient_id LIKE ? OR name LIKE ? OR phone LIKE ? ORDER BY created_at DESC",
            (term, term, term),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT id, patient_id, name, age, gender, phone, email, address, emergency_contact, insurance_provider, policy_number, past_illnesses, surgeries, allergies, family_history, created_at FROM patients ORDER BY created_at DESC"
        ).fetchall()
    conn.close()

    result = []
    for r in rows:
        result.append({
            "id": r[0], "patient_id": r[1], "name": r[2], "age": r[3], "gender": r[4],
            "phone": r[5], "email": r[6], "address": r[7], "emergency_contact": r[8],
            "insurance_provider": r[9], "policy_number": r[10],
            "past_illnesses": json.loads(r[11] or "[]"), "surgeries": json.loads(r[12] or "[]"),
            "allergies": json.loads(r[13] or "[]"), "family_history": json.loads(r[14] or "[]"),
            "created_at": r[15],
        })
    return result


async def get_patient_db(patient_id: str) -> Optional[dict]:
    patients = await list_patients_db(search_term=patient_id)
    for p in patients:
        if p["patient_id"] == patient_id or p["id"] == patient_id:
            return p
    return None


# --- Appointment CRUD ---
async def save_appointment_db(data: dict) -> dict:
    record = {
        "id": str(uuid4()),
        "patient_id": data["patient_id"],
        "patient_name": data["patient_name"],
        "doctor_name": data["doctor_name"],
        "department": data["department"],
        "appointment_date": data["appointment_date"],
        "appointment_time": data["appointment_time"],
        "appointment_type": data.get("appointment_type", "Scheduled"),
        "token_number": data.get("token_number") or random.randint(1, 50),
        "notes": data.get("notes", ""),
        "status": "Booked",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    conn = _connect_sqlite()
    conn.execute(
        """
        INSERT INTO appointments (id, patient_id, patient_name, doctor_name, department, appointment_date, appointment_time, appointment_type, token_number, notes, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (record["id"], record["patient_id"], record["patient_name"], record["doctor_name"], record["department"], record["appointment_date"], record["appointment_time"], record["appointment_type"], record["token_number"], record["notes"], record["status"], record["created_at"]),
    )
    conn.commit()
    conn.close()

    if db is not None:
        try:
            await db.appointments.insert_one(record)
        except Exception:
            pass
    return record


async def list_appointments_db(doctor_name: Optional[str] = None, status: Optional[str] = None) -> List[dict]:
    conn = _connect_sqlite()
    rows = conn.execute("SELECT id, patient_id, patient_name, doctor_name, department, appointment_date, appointment_time, appointment_type, token_number, notes, status, created_at FROM appointments ORDER BY created_at DESC").fetchall()
    conn.close()

    result = []
    for r in rows:
        item = {
            "id": r[0], "patient_id": r[1], "patient_name": r[2], "doctor_name": r[3],
            "department": r[4], "appointment_date": r[5], "appointment_time": r[6],
            "appointment_type": r[7], "token_number": r[8], "notes": r[9], "status": r[10],
            "created_at": r[11],
        }
        if doctor_name and doctor_name.lower() not in item["doctor_name"].lower():
            continue
        if status and status.lower() != item["status"].lower():
            continue
        result.append(item)
    return result


async def update_appointment_status_db(appointment_id: str, status: str) -> Optional[dict]:
    conn = _connect_sqlite()
    conn.execute("UPDATE appointments SET status = ? WHERE id = ?", (status, appointment_id))
    conn.commit()
    conn.close()
    apps = await list_appointments_db()
    for a in apps:
        if a["id"] == appointment_id:
            return a
    return None


# --- Lab Orders CRUD ---
async def save_lab_order_db(data: dict) -> dict:
    record = {
        "id": str(uuid4()),
        "patient_id": data["patient_id"],
        "patient_name": data["patient_name"],
        "test_name": data["test_name"],
        "ordering_doctor": data["ordering_doctor"],
        "department": data["department"],
        "notes": data.get("notes", ""),
        "status": "Ordered",
        "result_value": None,
        "reference_range": "Normal",
        "abnormal_flag": "NORMAL",
        "completed_at": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    conn = _connect_sqlite()
    conn.execute(
        """
        INSERT INTO lab_orders (id, patient_id, patient_name, test_name, ordering_doctor, department, notes, status, result_value, reference_range, abnormal_flag, completed_at, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (record["id"], record["patient_id"], record["patient_name"], record["test_name"], record["ordering_doctor"], record["department"], record["notes"], record["status"], record["result_value"], record["reference_range"], record["abnormal_flag"], record["completed_at"], record["created_at"]),
    )
    conn.commit()
    conn.close()
    return record


async def list_lab_orders_db(patient_id: Optional[str] = None, status: Optional[str] = None) -> List[dict]:
    conn = _connect_sqlite()
    rows = conn.execute("SELECT id, patient_id, patient_name, test_name, ordering_doctor, department, notes, status, result_value, reference_range, abnormal_flag, completed_at, created_at FROM lab_orders ORDER BY created_at DESC").fetchall()
    conn.close()

    result = []
    for r in rows:
        item = {
            "id": r[0], "patient_id": r[1], "patient_name": r[2], "test_name": r[3],
            "ordering_doctor": r[4], "department": r[5], "notes": r[6], "status": r[7],
            "result_value": r[8], "reference_range": r[9], "abnormal_flag": r[10],
            "completed_at": r[11], "created_at": r[12],
        }
        if patient_id and patient_id != item["patient_id"]:
            continue
        if status and status.lower() != item["status"].lower():
            continue
        result.append(item)
    return result


async def update_lab_result_db(order_id: str, result_value: str, reference_range: str, abnormal_flag: str) -> Optional[dict]:
    now = datetime.now(timezone.utc).isoformat()
    conn = _connect_sqlite()
    conn.execute(
        "UPDATE lab_orders SET status = 'Completed', result_value = ?, reference_range = ?, abnormal_flag = ?, completed_at = ? WHERE id = ?",
        (result_value, reference_range, abnormal_flag, now, order_id),
    )
    conn.commit()
    conn.close()
    orders = await list_lab_orders_db()
    for o in orders:
        if o["id"] == order_id:
            return o
    return None


# --- Prescriptions & Pharmacy CRUD ---
async def save_prescription_db(data: dict) -> dict:
    record = {
        "id": str(uuid4()),
        "patient_id": data["patient_id"],
        "patient_name": data["patient_name"],
        "doctor_name": data["doctor_name"],
        "medication_name": data["medication_name"],
        "dosage": data["dosage"],
        "frequency": data["frequency"],
        "duration": data["duration"],
        "special_instructions": data.get("special_instructions", ""),
        "dispensed": False,
        "dispensed_at": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    conn = _connect_sqlite()
    conn.execute(
        """
        INSERT INTO prescriptions (id, patient_id, patient_name, doctor_name, medication_name, dosage, frequency, duration, special_instructions, dispensed, dispensed_at, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, NULL, ?)
        """,
        (record["id"], record["patient_id"], record["patient_name"], record["doctor_name"], record["medication_name"], record["dosage"], record["frequency"], record["duration"], record["special_instructions"], record["created_at"]),
    )
    conn.commit()
    conn.close()
    return record


async def list_prescriptions_db(patient_id: Optional[str] = None) -> List[dict]:
    conn = _connect_sqlite()
    rows = conn.execute("SELECT id, patient_id, patient_name, doctor_name, medication_name, dosage, frequency, duration, special_instructions, dispensed, dispensed_at, created_at FROM prescriptions ORDER BY created_at DESC").fetchall()
    conn.close()

    result = []
    for r in rows:
        item = {
            "id": r[0], "patient_id": r[1], "patient_name": r[2], "doctor_name": r[3],
            "medication_name": r[4], "dosage": r[5], "frequency": r[6], "duration": r[7],
            "special_instructions": r[8], "dispensed": bool(r[9]), "dispensed_at": r[10],
            "created_at": r[11],
        }
        if patient_id and patient_id != item["patient_id"]:
            continue
        result.append(item)
    return result


async def dispense_prescription_db(rx_id: str) -> Optional[dict]:
    now = datetime.now(timezone.utc).isoformat()
    conn = _connect_sqlite()
    conn.execute("UPDATE prescriptions SET dispensed = 1, dispensed_at = ? WHERE id = ?", (now, rx_id))
    conn.commit()
    conn.close()
    rxs = await list_prescriptions_db()
    for r in rxs:
        if r["id"] == rx_id:
            return r
    return None


async def list_pharmacy_inventory_db() -> List[dict]:
    return [
        {"medication_name": "Aspirin 325mg", "category": "Analgesic / Antiplatelet", "stock_quantity": 450, "unit_price": 0.50, "status": "IN_STOCK"},
        {"medication_name": "Metformin 500mg", "category": "Antidiabetic", "stock_quantity": 380, "unit_price": 0.80, "status": "IN_STOCK"},
        {"medication_name": "Metoprolol 50mg", "category": "Beta Blocker", "stock_quantity": 120, "unit_price": 1.20, "status": "IN_STOCK"},
        {"medication_name": "Amoxicillin 500mg", "category": "Antibiotic", "stock_quantity": 18, "unit_price": 2.50, "status": "LOW_STOCK"},
        {"medication_name": "Atorvastatin 20mg", "category": "Statin", "stock_quantity": 290, "unit_price": 1.50, "status": "IN_STOCK"},
        {"medication_name": "Albuterol Inhaler", "category": "Bronchodilator", "stock_quantity": 8, "unit_price": 25.00, "status": "CRITICAL_LOW"},
    ]


# --- Billing & Invoices CRUD ---
async def save_invoice_db(data: dict) -> dict:
    total = float(data.get("consultation_fee", 0)) + float(data.get("lab_fee", 0)) + float(data.get("pharmacy_fee", 0)) + float(data.get("room_charges", 0))
    record = {
        "id": str(uuid4()),
        "patient_id": data["patient_id"],
        "patient_name": data["patient_name"],
        "consultation_fee": float(data.get("consultation_fee", 0)),
        "lab_fee": float(data.get("lab_fee", 0)),
        "pharmacy_fee": float(data.get("pharmacy_fee", 0)),
        "room_charges": float(data.get("room_charges", 0)),
        "total_amount": total,
        "payment_status": "Pending",
        "insurance_claim_amount": float(data.get("insurance_claim_amount", 0)),
        "insurance_status": data.get("insurance_status", "Not Submitted"),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    conn = _connect_sqlite()
    conn.execute(
        """
        INSERT INTO invoices (id, patient_id, patient_name, consultation_fee, lab_fee, pharmacy_fee, room_charges, total_amount, payment_status, insurance_claim_amount, insurance_status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (record["id"], record["patient_id"], record["patient_name"], record["consultation_fee"], record["lab_fee"], record["pharmacy_fee"], record["room_charges"], record["total_amount"], record["payment_status"], record["insurance_claim_amount"], record["insurance_status"], record["created_at"]),
    )
    conn.commit()
    conn.close()
    return record


async def list_invoices_db(patient_id: Optional[str] = None, status: Optional[str] = None) -> List[dict]:
    conn = _connect_sqlite()
    rows = conn.execute("SELECT id, patient_id, patient_name, consultation_fee, lab_fee, pharmacy_fee, room_charges, total_amount, payment_status, insurance_claim_amount, insurance_status, created_at FROM invoices ORDER BY created_at DESC").fetchall()
    conn.close()

    result = []
    for r in rows:
        item = {
            "id": r[0], "patient_id": r[1], "patient_name": r[2], "consultation_fee": r[3],
            "lab_fee": r[4], "pharmacy_fee": r[5], "room_charges": r[6], "total_amount": r[7],
            "payment_status": r[8], "insurance_claim_amount": r[9], "insurance_status": r[10],
            "created_at": r[11],
        }
        if patient_id and patient_id != item["patient_id"]:
            continue
        if status and status.lower() != item["payment_status"].lower():
            continue
        result.append(item)
    return result


async def update_invoice_payment_db(invoice_id: str, payment_status: str, insurance_status: str) -> Optional[dict]:
    conn = _connect_sqlite()
    conn.execute("UPDATE invoices SET payment_status = ?, insurance_status = ? WHERE id = ?", (payment_status, insurance_status, invoice_id))
    conn.commit()
    conn.close()
    invs = await list_invoices_db()
    for i in invs:
        if i["id"] == invoice_id:
            return i
    return None


# --- Staff Management CRUD ---
async def save_staff_member_db(data: dict) -> dict:
    record = {
        "id": str(uuid4()),
        "name": data["name"],
        "role": data["role"],
        "department": data["department"],
        "shift": data.get("shift", "Morning"),
        "phone": data.get("phone", ""),
        "email": data.get("email", ""),
        "status": "Active",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    conn = _connect_sqlite()
    conn.execute(
        "INSERT INTO staff (id, name, role, department, shift, phone, email, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (record["id"], record["name"], record["role"], record["department"], record["shift"], record["phone"], record["email"], record["status"], record["created_at"]),
    )
    conn.commit()
    conn.close()
    return record


async def list_staff_members_db(department: Optional[str] = None, role: Optional[str] = None) -> List[dict]:
    conn = _connect_sqlite()
    rows = conn.execute("SELECT id, name, role, department, shift, phone, email, status, created_at FROM staff ORDER BY created_at DESC").fetchall()
    conn.close()

    result = []
    for r in rows:
        item = {
            "id": r[0], "name": r[1], "role": r[2], "department": r[3],
            "shift": r[4], "phone": r[5], "email": r[6], "status": r[7], "created_at": r[8],
        }
        if department and department.lower() not in item["department"].lower():
            continue
        if role and role.lower() not in item["role"].lower():
            continue
        result.append(item)
    return result


# --- Consumables & Inventory CRUD ---
async def save_consumable_db(data: dict) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    record = {
        "id": str(uuid4()),
        "item_name": data["item_name"],
        "category": data["category"],
        "quantity": int(data["quantity"]),
        "reorder_level": int(data.get("reorder_level", 20)),
        "unit_cost": float(data.get("unit_cost", 0)),
        "vendor_name": data.get("vendor_name", "Medical Supplies Co."),
        "updated_at": now,
    }
    conn = _connect_sqlite()
    conn.execute(
        "INSERT OR REPLACE INTO consumables (id, item_name, category, quantity, reorder_level, unit_cost, vendor_name, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (record["id"], record["item_name"], record["category"], record["quantity"], record["reorder_level"], record["unit_cost"], record["vendor_name"], record["updated_at"]),
    )
    conn.commit()
    conn.close()
    return record


async def list_consumables_db(category: Optional[str] = None) -> List[dict]:
    conn = _connect_sqlite()
    rows = conn.execute("SELECT id, item_name, category, quantity, reorder_level, unit_cost, vendor_name, updated_at FROM consumables ORDER BY updated_at DESC").fetchall()
    conn.close()

    result = []
    for r in rows:
        item = {
            "id": r[0], "item_name": r[1], "category": r[2], "quantity": r[3],
            "reorder_level": r[4], "unit_cost": r[5], "vendor_name": r[6], "updated_at": r[7],
        }
        if category and category.lower() not in item["category"].lower():
            continue
        result.append(item)

    if not result:
        # Initial seed supplies
        return [
            {"id": "c1", "item_name": "Disposable Syringes 5ml", "category": "Surgical Supplies", "quantity": 1200, "reorder_level": 200, "unit_cost": 0.25, "vendor_name": "MedSurge Inc.", "updated_at": datetime.now(timezone.utc).isoformat()},
            {"id": "c2", "item_name": "IV Cannula 20G", "category": "Infusion Supplies", "quantity": 15, "reorder_level": 50, "unit_cost": 1.50, "vendor_name": "CareTech Health", "updated_at": datetime.now(timezone.utc).isoformat()},
            {"id": "c3", "item_name": "Surgical Gloves (Medium)", "category": "PPE", "quantity": 500, "reorder_level": 100, "unit_cost": 0.40, "vendor_name": "SafeHand Medical", "updated_at": datetime.now(timezone.utc).isoformat()},
            {"id": "c4", "item_name": "Medical Oxygen Cylinder (Type D)", "category": "Respiratory", "quantity": 4, "reorder_level": 10, "unit_cost": 45.00, "vendor_name": "GasCorp Healthcare", "updated_at": datetime.now(timezone.utc).isoformat()},
        ]
    return result