from typing import Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.auth import get_current_user
from app.database.mongodb import (
    check_duplicate_report_db,
    delete_report_db,
    get_analytics_db,
    get_report_db,
    list_activity_logs_db,
    list_reports_db,
    save_activity_log_db,
    save_report_db,
)
from app.schemas.extraction import (
    ActivityLog,
    AnalyticsSummary,
    DuplicateCheckResponse,
    ReportCreate,
    ReportResponse,
)
from app.services.nlp_service import compute_text_hash

router = APIRouter(prefix="/reports", tags=["Reports"])


def _build_report(payload: ReportCreate, username: str) -> Dict[str, object]:
    text_hash = payload.report_hash or compute_text_hash(payload.report_text)
    return {
        "id": str(uuid4()),
        "username": username,
        "report_hash": text_hash,
        "patient_id": payload.patient_id or f"PAT-2026-{uuid4().hex[:4].upper()}",
        "patient_name": payload.patient_name,
        "age": payload.age,
        "gender": payload.gender,
        "room_number": payload.room_number or "Ward 1",
        "admission_status": payload.admission_status or "Admitted",
        "triage_level": payload.triage_level or "Routine",
        "attending_physician": payload.attending_physician or "Dr. N. Patel",
        "risk_level": payload.risk_level or "Low",
        "clinical_flags": payload.clinical_flags or [],
        "report_text": payload.report_text,
        "diagnoses": payload.diagnoses,
        "symptoms": payload.symptoms,
        "medications": payload.medications,
        "dosages": payload.dosages,
        "allergies": payload.allergies,
        "lab_tests": payload.lab_tests,
        "department": payload.department or "General Medicine",
        "icd10_code": payload.icd10_code or "R50.9",
        "confidence_score": payload.confidence_score or 0.85,
    }


@router.post("/check-duplicate", response_model=DuplicateCheckResponse)
async def check_duplicate(payload: Dict[str, str], username: str = Depends(get_current_user)):
    report_text = payload.get("report_text", "")
    if not report_text:
        return DuplicateCheckResponse(is_duplicate=False, message="No text provided")

    h = compute_text_hash(report_text)
    existing = await check_duplicate_report_db(username, h)
    if existing:
        return DuplicateCheckResponse(
            is_duplicate=True,
            existing_report_id=existing["id"],
            message="Duplicate report detected in patient history.",
        )

    return DuplicateCheckResponse(is_duplicate=False, message="Unique report text.")


@router.post("/", response_model=ReportResponse)
async def create_report(payload: ReportCreate, username: str = Depends(get_current_user)):
    report = _build_report(payload, username)
    saved = await save_report_db(report)

    # Record activity log
    p_info = report.get("patient_name") or report.get("patient_id")
    await save_activity_log_db(
        username,
        "REPORT_SAVED",
        f"Saved {report.get('department')} note for {p_info} (ICD-10: {report.get('icd10_code')})"
    )

    return saved


@router.get("/", response_model=List[ReportResponse])
async def list_reports(
    search: Optional[str] = Query(None, description="Search term across patient ID, name, text, and entities"),
    department: Optional[str] = Query(None, description="Filter by department"),
    triage_level: Optional[str] = Query(None, description="Filter by triage level"),
    admission_status: Optional[str] = Query(None, description="Filter by admission status"),
    username: str = Depends(get_current_user),
):
    return await list_reports_db(
        username,
        search=search,
        department=department,
        triage_level=triage_level,
        admission_status=admission_status,
    )


@router.get("/activity-logs", response_model=List[ActivityLog])
async def get_activity_logs(username: str = Depends(get_current_user)):
    return await list_activity_logs_db(username)


@router.get("/analytics", response_model=AnalyticsSummary)
async def get_analytics(username: str = Depends(get_current_user)):
    return await get_analytics_db(username)


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(report_id: str, username: str = Depends(get_current_user)):
    report = await get_report_db(report_id, username)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.delete("/{report_id}")
async def delete_report(report_id: str, username: str = Depends(get_current_user)):
    success = await delete_report_db(report_id, username)
    if not success:
        raise HTTPException(status_code=404, detail="Report not found or could not be deleted")

    await save_activity_log_db(username, "REPORT_DELETED", f"Deleted report ID: {report_id}")
    return {"message": "Report deleted successfully", "id": report_id}
