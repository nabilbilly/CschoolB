from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Optional, List
from .models import Gender

class GuardianBase(BaseModel):
    name: str
    relationship_type: str
    phone: str
    secondary_phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: str
    occupation: Optional[str] = None

class GuardianCreate(GuardianBase):
    pass

class GuardianUpdate(BaseModel):
    name: Optional[str] = None
    relationship_type: Optional[str] = None
    phone: Optional[str] = None
    secondary_phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    occupation: Optional[str] = None

class GuardianResponse(GuardianBase):
    id: int
    student_id: int

    class Config:
        from_attributes = True

class StudentMedicalBase(BaseModel):
    health_conditions: Optional[str] = None
    allergies: Optional[str] = None
    special_needs: Optional[str] = None

class StudentMedicalCreate(StudentMedicalBase):
    pass

class StudentMedicalUpdate(StudentMedicalBase):
    pass

class StudentMedicalResponse(StudentMedicalBase):
    id: int
    student_id: int

    class Config:
        from_attributes = True

class StudentAccountBase(BaseModel):
    username: str
    must_change_password: bool = True
    is_active: bool = False

class StudentAccountResponse(StudentAccountBase):
    id: int
    student_id: int

    class Config:
        from_attributes = True

class StudentLogin(BaseModel):
    username: str # This can be their index_number or generated username
    password: str

class StudentPasswordChange(BaseModel):
    current_password: str
    new_password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    must_change_password: bool
    student_name: str
    index_number: str

class StudentBase(BaseModel):
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    gender: Gender
    date_of_birth: date
    nationality: str
    address: Optional[str] = None
    city: Optional[str] = None
    photo: Optional[str] = None

class StudentCreate(StudentBase):
    pass

class StudentUpdate(BaseModel):
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    gender: Optional[Gender] = None
    date_of_birth: Optional[date] = None
    nationality: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    photo: Optional[str] = None
    index_number: Optional[str] = None
    class_id: Optional[int] = None
    stream_id: Optional[int] = None

class StudentResponse(StudentBase):
    id: int
    index_number: Optional[str] = None
    created_at: datetime
    guardians: List[GuardianResponse] = []
    medical: Optional[StudentMedicalResponse] = None
    account: Optional[StudentAccountResponse] = None
    
    # Dynamic fields from relationship/property
    current_class: Optional[str] = "N/A"
    current_stream: Optional[str] = "N/A"
    status: str = "Active"
    admission_year: Optional[str] = "N/A"
    class_id: Optional[int] = None
    stream_id: Optional[int] = None
    ghana_card: Optional[str] = None
    disability_status: Optional[str] = None
    pending_admission_id: Optional[int] = None

    class Config:
        from_attributes = True
