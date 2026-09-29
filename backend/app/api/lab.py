from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from app.api.auth import get_current_user
from app.schemas.extraction import LabOrderCreate, LabOrderResponse, LabResultUpdate
from app.database.mongodb import (
    save_lab_order_db,
    list_lab_orders_db,
    update_lab_result_db,
    save_activity_log_db,
)

router = APIRouter(prefix="/lab", tags=["Lab"])


@router.post("/orders", response_model=LabOrderResponse)
async def create_lab_order(payload: LabOrderCreate, username: str = Depends(get_current_user)):
    lab_order = await save_lab_order_db(payload.model_dump())
    await save_activity_log_db(username, "CREATE_LAB_ORDER", f"Ordered {payload.test_name} for patient {payload.patient_name}")
    return LabOrderResponse(**lab_order)


@router.get("/orders", response_model=List[LabOrderResponse])
async def list_lab_orders(
    patient_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    username: str = Depends(get_current_user),
):
    orders = await list_lab_orders_db(patient_id=patient_id, status=status)
    return [LabOrderResponse(**o) for o in orders]


@router.patch("/orders/{order_id}/result", response_model=LabOrderResponse)
@router.put("/orders/{order_id}/result", response_model=LabOrderResponse)
async def enter_lab_result(
    order_id: str,
    payload: LabResultUpdate,
    username: str = Depends(get_current_user),
):
    ref = payload.normal_range or "Normal"
    flag = payload.flag or "NORMAL"
    updated = await update_lab_result_db(order_id, payload.result_value, ref, flag)
    if not updated:
        raise HTTPException(status_code=404, detail="Lab order not found")
    await save_activity_log_db(username, "ENTER_LAB_RESULT", f"Entered result '{payload.result_value}' ({flag}) for lab order {order_id}")
    return LabOrderResponse(**updated)
