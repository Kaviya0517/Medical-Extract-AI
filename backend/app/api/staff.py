from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from app.api.auth import get_current_user
from app.schemas.extraction import StaffMemberCreate, StaffMemberResponse
from app.database.mongodb import (
    save_staff_member_db,
    list_staff_members_db,
    save_activity_log_db,
)

router = APIRouter(prefix="/staff", tags=["Staff"])


@router.post("/", response_model=StaffMemberResponse)
async def create_staff_member(payload: StaffMemberCreate, username: str = Depends(get_current_user)):
    staff = await save_staff_member_db(payload.model_dump())
    await save_activity_log_db(username, "CREATE_STAFF", f"Added staff member {payload.name} ({payload.role} - {payload.department})")
    return StaffMemberResponse(**staff)


@router.get("/", response_model=List[StaffMemberResponse])
async def list_staff_members(
    department: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    username: str = Depends(get_current_user),
):
    staff_list = await list_staff_members_db(department=department, role=role)
    return [StaffMemberResponse(**s) for s in staff_list]
