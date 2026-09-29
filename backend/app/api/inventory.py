from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from app.api.auth import get_current_user
from app.schemas.extraction import ConsumableCreate, ConsumableResponse
from app.database.mongodb import (
    save_consumable_db,
    list_consumables_db,
    save_activity_log_db,
)

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.post("/consumables", response_model=ConsumableResponse)
async def create_consumable(payload: ConsumableCreate, username: str = Depends(get_current_user)):
    item = await save_consumable_db(payload.model_dump())
    await save_activity_log_db(username, "ADD_CONSUMABLE", f"Added supply item {payload.item_name} ({payload.quantity} units)")
    return ConsumableResponse(**item)


@router.get("/consumables", response_model=List[ConsumableResponse])
async def list_consumables(
    category: Optional[str] = Query(None),
    username: str = Depends(get_current_user),
):
    items = await list_consumables_db(category=category)
    return [ConsumableResponse(**i) for i in items]
