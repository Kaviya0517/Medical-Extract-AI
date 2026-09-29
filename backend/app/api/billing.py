from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from app.api.auth import get_current_user
from app.schemas.extraction import InvoiceCreate, InvoiceResponse
from app.database.mongodb import (
    save_invoice_db,
    list_invoices_db,
    update_invoice_payment_db,
    save_activity_log_db,
)

router = APIRouter(prefix="/billing", tags=["Billing"])


@router.post("/invoices", response_model=InvoiceResponse)
async def create_invoice(payload: InvoiceCreate, username: str = Depends(get_current_user)):
    invoice = await save_invoice_db(payload.model_dump())
    await save_activity_log_db(username, "CREATE_INVOICE", f"Generated invoice of ${invoice['total_amount']} for patient {payload.patient_name}")
    return InvoiceResponse(**invoice)


@router.get("/invoices", response_model=List[InvoiceResponse])
async def list_invoices(
    patient_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    username: str = Depends(get_current_user),
):
    invoices = await list_invoices_db(patient_id=patient_id, status=status)
    return [InvoiceResponse(**inv) for inv in invoices]


@router.put("/invoices/{invoice_id}/payment", response_model=InvoiceResponse)
async def record_payment(
    invoice_id: str,
    payment_status: str = "Paid",  # Paid, Pending, Partial
    insurance_status: str = "Approved",
    username: str = Depends(get_current_user),
):
    updated = await update_invoice_payment_db(invoice_id, payment_status, insurance_status)
    if not updated:
        raise HTTPException(status_code=404, detail="Invoice not found")
    await save_activity_log_db(username, "RECORD_PAYMENT", f"Recorded payment status '{payment_status}' for invoice {invoice_id}")
    return InvoiceResponse(**updated)
