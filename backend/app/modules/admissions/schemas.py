from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from .models import AdmissionStatus
from ..students.schemas import StudentCreate, GuardianCreate, StudentMedicalCreate

class AdmissionBase(BaseModel):
    student_id: int
    academic_year_id: int
    class_id: int
    stream_id: Optional[int] = None
    term_id: int
    voucher_id: int
    status: AdmissionStatus = AdmissionStatus.PENDING

class AdmissionCreate(AdmissionBase):
    pass

class AdmissionWizardSubmit(BaseModel):
    voucher_session_token: str
    student: StudentCreate
    guardians: List[GuardianCreate]
    medical: Optional[StudentMedicalCreate] = None
    placement: dict # {academic_year_id, class_id, stream_id, term_id}

class AdmissionUpdate(BaseModel):
    class_id: Optional[int] = None
    stream_id: Optional[int] = None
    status: Optional[AdmissionStatus] = None
    approved_by_admin_id: Optional[int] = None
    approved_at: Optional[datetime] = None

class AdmissionResponse(AdmissionBase):
    id: int
    student_name: Optional[str] = None
    voucher_number: Optional[str] = None
    class_name: Optional[str] = None
    academic_year_name: Optional[str] = None
    term_name: Optional[str] = None
    approved_by_admin_id: Optional[int] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    temp_password: Optional[str] = None
    student_index_number: Optional[str] = None

    class Config:
        from_attributes = True
