from sqlalchemy import Column, Integer, String, Enum as SqlEnum, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from app.db.base_class import Base

class VoucherStatus(str, enum.Enum):
    Unused = "Unused"
    Reserved = "Reserved"
    Used = "Used"
    Expired = "Expired"
    Revoked = "Revoked"

class VoucherAttemptResult(str, enum.Enum):
    Valid = "Valid"
    InvalidPin = "Invalid Pin"
    NotFound = "Not Found"
    Expired = "Expired"
    Used = "Used"
    Reserved = "Reserved"

class EVoucher(Base):
    id = Column(Integer, primary_key=True, index=True)
    voucher_number = Column(String, unique=True, index=True, nullable=False)
    pin_hash = Column(String, nullable=False)
    academic_year_id = Column(Integer, ForeignKey("academicyear.id"), nullable=False)
    status = Column(SqlEnum(VoucherStatus, values_callable=lambda x: [e.value for e in x]), default=VoucherStatus.UNUSED)
    
    expires_at = Column(DateTime, nullable=False)
    reserved_at = Column(DateTime, nullable=True)
    reserved_session_id = Column(String, nullable=True, index=True)
    
    used_at = Column(DateTime, nullable=True)
    used_by_student_id = Column(Integer, ForeignKey("student.id"), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by_admin_id = Column(Integer, nullable=True) # Will link to user later
    
    academic_year = relationship("AcademicYear")
    used_by_student = relationship("Student")
    admission = relationship("Admission", back_populates="voucher", uselist=False)

class VoucherAttemptLog(Base):
    id = Column(Integer, primary_key=True, index=True)
    voucher_number_entered = Column(String, index=True)
    ip_address = Column(String)
    user_agent = Column(String)
    result = Column(SqlEnum(VoucherAttemptResult, values_callable=lambda x: [e.value for e in x]))
    created_at = Column(DateTime, default=datetime.utcnow)
