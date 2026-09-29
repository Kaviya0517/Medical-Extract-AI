from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from app.api.auth import get_current_user
from app.schemas.extraction import AppointmentCreate, AppointmentResponse
from app.database.mongodb import (
    save_appointment_db,
    list_appointments_db,
    update_appointment_status_db,
    save_activity_log_db,
)

router = APIRouter(prefix="/appointments", tags=["Appointments"])


@router.post("/", response_model=AppointmentResponse)
async def create_appointment(payload: AppointmentCreate, username: str = Depends(get_current_user)):
    appointment = await save_appointment_db(payload.model_dump())
    await save_activity_log_db(username, "CREATE_APPOINTMENT", f"Booked {payload.appointment_type} appointment for {payload.patient_name} with {payload.doctor_name}")
    return AppointmentResponse(**appointment)


@router.get("/", response_model=List[AppointmentResponse])
async def list_appointments(
    doctor_name: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    username: str = Depends(get_current_user),
):
    appointments = await list_appointments_db(doctor_name=doctor_name, status=status)
    return [AppointmentResponse(**a) for a in appointments]


@router.put("/{appointment_id}/status", response_model=AppointmentResponse)
async def update_status(appointment_id: str, status: str, username: str = Depends(get_current_user)):
    updated = await update_appointment_status_db(appointment_id, status)
    if not updated:
        raise HTTPException(status_code=404, detail="Appointment not found")
    await save_activity_log_db(username, "UPDATE_APPOINTMENT_STATUS", f"Changed appointment {appointment_id} status to {status}")
    return AppointmentResponse(**updated)
