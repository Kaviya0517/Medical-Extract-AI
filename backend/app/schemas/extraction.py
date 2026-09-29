from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class Entity(BaseModel):
    text: str
    label: str
    start: Optional[int] = None
    end: Optional[int] = None


class ExtractionRequest(BaseModel):
    report_text: str
    patient_id: Optional[str] = None
    room_number: Optional[str] = None
    admission_status: Optional[str] = None
    attending_physician: Optional[str] = None


class ExtractionResponse(BaseModel):
    report_hash: Optional[str] = None
    patient_id: Optional[str] = None
    patient_name: Optional[str] = None
    age: Optional[str] = None
    gender: Optional[str] = None
    room_number: Optional[str] = None
    admission_status: Optional[str] = "Admitted"
    triage_level: Optional[str] = "Routine"
    attending_physician: Optional[str] = None
    risk_level: Optional[str] = "Low"
    clinical_flags: List[str] = Field(default_factory=list)
    diagnoses: List[str] = Field(default_factory=list)
    symptoms: List[str] = Field(default_factory=list)
    medications: List[str] = Field(default_factory=list)
    dosages: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    lab_tests: List[str] = Field(default_factory=list)
    raw_entities: List[Entity] = Field(default_factory=list)
    department: Optional[str] = "General Medicine"
    icd10_code: Optional[str] = "R50.9"
    cpt_code: Optional[str] = "CPT-99214"
    cpt_description: Optional[str] = "Office/Outpatient Visit"
    vitals: Optional[Dict[str, Any]] = Field(default_factory=dict)
    confidence_score: Optional[float] = 0.85


class UserRegister(BaseModel):
    username: str
    email: str
    password: str
    role: Optional[str] = "Doctor"
    hospital_name: Optional[str] = "General Medical Center"


class UserLogin(BaseModel):
    username: str
    password: str


class PasswordReset(BaseModel):
    username: str
    new_password: str


class UserProfile(BaseModel):
    username: str
    email: str
    role: str = "Doctor"
    hospital_name: str = "General Medical Center"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str = "Doctor"
    hospital_name: str = "General Medical Center"


class HospitalNameUpdate(BaseModel):
    hospital_name: str


class ReportCreate(BaseModel):
    report_hash: Optional[str] = None
    patient_id: Optional[str] = None
    patient_name: Optional[str] = None
    age: Optional[str] = None
    gender: Optional[str] = None
    room_number: Optional[str] = None
    admission_status: Optional[str] = "Admitted"
    triage_level: Optional[str] = "Routine"
    attending_physician: Optional[str] = None
    risk_level: Optional[str] = "Low"
    clinical_flags: List[str] = Field(default_factory=list)
    report_text: str
    diagnoses: List[str] = Field(default_factory=list)
    symptoms: List[str] = Field(default_factory=list)
    medications: List[str] = Field(default_factory=list)
    dosages: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    lab_tests: List[str] = Field(default_factory=list)
    department: Optional[str] = "General Medicine"
    icd10_code: Optional[str] = "R50.9"
    cpt_code: Optional[str] = "CPT-99214"
    cpt_description: Optional[str] = "Office/Outpatient Visit"
    vitals: Optional[Dict[str, Any]] = Field(default_factory=dict)
    confidence_score: Optional[float] = 0.85


class ReportResponse(ReportCreate):
    id: str
    username: str


class PatientCreate(BaseModel):
    patient_id: Optional[str] = None
    name: str
    age: str
    gender: str
    phone: str
    email: Optional[str] = ""
    address: Optional[str] = ""
    emergency_contact: Optional[str] = ""
    insurance_provider: Optional[str] = ""
    policy_number: Optional[str] = ""
    past_illnesses: List[str] = Field(default_factory=list)
    surgeries: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    family_history: List[str] = Field(default_factory=list)


class PatientResponse(PatientCreate):
    id: str
    created_at: str


class AppointmentCreate(BaseModel):
    patient_id: str
    patient_name: str
    doctor_name: str
    department: str
    appointment_date: str
    appointment_time: str
    appointment_type: str = "Scheduled"  # Scheduled or Walk-in
    token_number: Optional[int] = None
    notes: Optional[str] = ""


class AppointmentResponse(AppointmentCreate):
    id: str
    status: str = "Booked"  # Booked, In-Consultation, Completed, Cancelled
    created_at: str


class LabOrderCreate(BaseModel):
    patient_id: str
    patient_name: str
    test_name: str
    ordering_doctor: str
    department: str
    notes: Optional[str] = ""


class LabOrderResponse(LabOrderCreate):
    id: str
    status: str = "Ordered"  # Ordered, Processing, Completed
    result_value: Optional[str] = None
    reference_range: Optional[str] = None
    abnormal_flag: Optional[str] = None  # NORMAL, HIGH, LOW, CRITICAL
    completed_at: Optional[str] = None
    created_at: str


class LabResultUpdate(BaseModel):
    result_value: str
    normal_range: Optional[str] = "Normal"
    flag: Optional[str] = "NORMAL"
    status: Optional[str] = "Completed"


class PrescriptionCreate(BaseModel):
    patient_id: str
    patient_name: str
    doctor_name: str
    medication_name: str
    dosage: str
    frequency: str
    duration: str
    special_instructions: Optional[str] = ""


class PrescriptionResponse(PrescriptionCreate):
    id: str
    dispensed: bool = False
    dispensed_at: Optional[str] = None
    created_at: str


class InvoiceCreate(BaseModel):
    patient_id: str
    patient_name: str
    consultation_fee: float = 0.0
    lab_fee: float = 0.0
    pharmacy_fee: float = 0.0
    room_charges: float = 0.0
    insurance_claim_amount: float = 0.0
    insurance_status: str = "Not Submitted"  # Not Submitted, Submitted, Approved, Denied


class InvoiceResponse(InvoiceCreate):
    id: str
    total_amount: float
    payment_status: str = "Pending"  # Pending, Paid, Partial
    created_at: str


class StaffMemberCreate(BaseModel):
    name: str
    role: str
    department: str
    shift: str = "Morning"  # Morning, Evening, Night
    phone: str
    email: str


class StaffMemberResponse(StaffMemberCreate):
    id: str
    status: str = "Active"
    created_at: str


class ConsumableCreate(BaseModel):
    item_name: str
    category: str
    quantity: int
    reorder_level: int = 20
    unit_cost: float
    vendor_name: str


class ConsumableResponse(ConsumableCreate):
    id: str
    updated_at: str


class AnalyticsItem(BaseModel):
    name: str
    count: int


class AnalyticsSummary(BaseModel):
    total_reports: int
    active_admitted: int = 0
    icu_patients: int = 0
    emergency_cases: int = 0
    critical_alerts_count: int = 0
    department_counts: Dict[str, int] = Field(default_factory=dict)
    triage_counts: Dict[str, int] = Field(default_factory=dict)
    risk_counts: Dict[str, int] = Field(default_factory=dict)
    top_diagnoses: List[AnalyticsItem] = Field(default_factory=list)
    top_symptoms: List[AnalyticsItem] = Field(default_factory=list)
    top_medications: List[AnalyticsItem] = Field(default_factory=list)
    avg_confidence: float = 0.0


class ActivityLog(BaseModel):
    id: str
    username: str
    action: str
    details: str
    timestamp: str


class DuplicateCheckResponse(BaseModel):
    is_duplicate: bool
    existing_report_id: Optional[str] = None
    message: str