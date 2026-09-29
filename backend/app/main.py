from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import extraction, auth, reports, patients, appointments, lab, pharmacy, billing, staff, inventory, fhir
from app.database.mongodb import check_db_status


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_info = await check_db_status()
    if db_info["mongodb_connected"]:
        print("✅ Connected to MongoDB Atlas")
    elif db_info["mongodb_configured"]:
        print("⚠️ MongoDB URL configured but connection failed; operating with SQLite fallback")
    else:
        print("ℹ️ MongoDB URL not configured; operating in local SQLite mode")
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(extraction.router)
app.include_router(auth.router)
app.include_router(reports.router)
app.include_router(patients.router)
app.include_router(appointments.router)
app.include_router(lab.router)
app.include_router(pharmacy.router)
app.include_router(billing.router)
app.include_router(staff.router)
app.include_router(inventory.router)
app.include_router(fhir.router)


@app.get("/health")
async def health():
    db_info = await check_db_status()
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": db_info,
    }


@app.get("/")
async def home():
    db_info = await check_db_status()
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "status": "Running Successfully",
        "database_mode": db_info["database_mode"],
    }