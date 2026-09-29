import hashlib
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt

from app.core.config import settings
from app.database.mongodb import get_user_db, save_user_db, update_user_hospital_name_db, reset_password_db
from app.schemas.extraction import TokenResponse, UserLogin, UserRegister, UserProfile, HospitalNameUpdate, PasswordReset


router = APIRouter(prefix="/auth", tags=["Auth"])
bearer_scheme = HTTPBearer()

_users_db: Dict[str, Dict[str, str]] = {}


@router.post("/reset-password")
async def reset_password(payload: PasswordReset):
    clean_username = payload.username.strip()
    if not clean_username or not payload.new_password:
        raise HTTPException(status_code=400, detail="Username and new password are required")

    hashed = _hash_password(payload.new_password)
    updated = await reset_password_db(clean_username, hashed)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Account '{clean_username}' not found.")
    return {"message": f"Password for '{clean_username}' updated successfully."}


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _verify_password(password: str, hashed_password: str) -> bool:
    return _hash_password(password) == hashed_password


def _create_access_token(username: str, role: str = "Doctor", hospital_name: str = "General Medical Center") -> str:
    payload = {
        "sub": username,
        "role": role,
        "hospital_name": hospital_name,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


@router.post("/register", response_model=TokenResponse)
async def register(payload: UserRegister):
    clean_username = payload.username.strip()
    if not clean_username:
        raise HTTPException(status_code=400, detail="Username cannot be empty")

    existing_user = await get_user_db(clean_username)
    if existing_user is not None or clean_username in _users_db:
        raise HTTPException(status_code=400, detail=f"Account '{clean_username}' already exists. Please click 'Sign in' below.")

    hashed = _hash_password(payload.password)
    role = payload.role or "Doctor"
    h_name = payload.hospital_name or "General Medical Center"
    await save_user_db(clean_username, payload.email, hashed, role, h_name)

    _users_db[clean_username] = {
        "email": payload.email,
        "password": hashed,
        "role": role,
        "hospital_name": h_name,
    }
    token = _create_access_token(clean_username, role=role, hospital_name=h_name)
    return TokenResponse(access_token=token, role=role, hospital_name=h_name)


@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin):
    clean_username = payload.username.strip()
    user = await get_user_db(clean_username)
    if not user and clean_username in _users_db:
        user = {
            "username": clean_username,
            "email": _users_db[clean_username]["email"],
            "password": _users_db[clean_username]["password"],
            "role": _users_db[clean_username].get("role", "Doctor"),
            "hospital_name": _users_db[clean_username].get("hospital_name", "General Medical Center"),
        }

    if not user:
        raise HTTPException(status_code=401, detail=f"Account '{clean_username}' not registered. Click 'Register Profile' below to create this account.")

    if not _verify_password(payload.password, user["password"]):
        raise HTTPException(status_code=401, detail=f"Incorrect password for staff account '{clean_username}'.")

    role = user.get("role", "Doctor")
    h_name = user.get("hospital_name", "General Medical Center")
    token = _create_access_token(clean_username, role=role, hospital_name=h_name)
    return TokenResponse(access_token=token, role=role, hospital_name=h_name)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> str:
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc

    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")
    return username


@router.get("/me", response_model=UserProfile)
async def get_me(username: str = Depends(get_current_user)):
    user = await get_user_db(username)
    if user:
        return UserProfile(
            username=username,
            email=user.get("email", ""),
            role=user.get("role", "Doctor"),
            hospital_name=user.get("hospital_name", "General Medical Center"),
        )
    return UserProfile(username=username, email="")


@router.put("/hospital-name", response_model=UserProfile)
async def update_hospital_name(
    payload: HospitalNameUpdate,
    username: str = Depends(get_current_user),
):
    h_name = payload.hospital_name.strip() or "General Medical Center"
    await update_user_hospital_name_db(username, h_name)
    user = await get_user_db(username)
    email = user.get("email", "") if user else ""
    role = user.get("role", "Doctor") if user else "Doctor"
    return UserProfile(username=username, email=email, role=role, hospital_name=h_name)
