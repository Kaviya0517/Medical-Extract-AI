from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from app.api.auth import get_current_user
from app.schemas.extraction import PrescriptionCreate, PrescriptionResponse
from app.database.mongodb import (
    save_prescription_db,
    list_prescriptions_db,
    dispense_prescription_db,
    list_pharmacy_inventory_db,
    save_activity_log_db,
)

router = APIRouter(prefix="/pharmacy", tags=["Pharmacy"])


@router.post("/prescriptions", response_model=PrescriptionResponse)
async def create_prescription(payload: PrescriptionCreate, username: str = Depends(get_current_user)):
    rx = await save_prescription_db(payload.model_dump())
    await save_activity_log_db(username, "CREATE_PRESCRIPTION", f"Prescribed {payload.medication_name} ({payload.dosage}) for patient {payload.patient_name}")
    return PrescriptionResponse(**rx)


@router.get("/prescriptions", response_model=List[PrescriptionResponse])
async def list_prescriptions(
    patient_id: Optional[str] = Query(None),
    username: str = Depends(get_current_user),
):
    rxs = await list_prescriptions_db(patient_id=patient_id)
    return [PrescriptionResponse(**r) for r in rxs]


@router.put("/prescriptions/{rx_id}/dispense", response_model=PrescriptionResponse)
async def dispense_prescription(rx_id: str, username: str = Depends(get_current_user)):
    dispensed = await dispense_prescription_db(rx_id)
    if not dispensed:
        raise HTTPException(status_code=404, detail="Prescription not found")
    await save_activity_log_db(username, "DISPENSE_MEDICATION", f"Dispensed prescription {rx_id}")
    return PrescriptionResponse(**dispensed)


@router.get("/inventory")
async def get_pharmacy_inventory(username: str = Depends(get_current_user)):
    return await list_pharmacy_inventory_db()
