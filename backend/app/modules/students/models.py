from sqlalchemy import Column, Integer, String, Date, Enum as SqlEnum, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
import enum
from typing import Optional
from datetime import datetime
from app.db.base_class import Base
from ..admissions.models import AdmissionStatus

class Gender(str, enum.Enum):
    Male = "Male"
    Female = "Female"

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            for member in cls:
                if member.value.upper() == value.upper():
                    return member
        return None

class Student(Base):
    id = Column(Integer, primary_key=True, index=True)
    index_number = Column(String, unique=True, index=True, nullable=True)
    first_name = Column(String, nullable=False)
    middle_name = Column(String, nullable=True)
    last_name = Column(String, nullable=False)
    gender = Column(SqlEnum(Gender, values_callable=lambda x: [e.value for e in x]), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    nationality = Column(String, nullable=False)
    address = Column(Text, nullable=True)
    city = Column(String, nullable=True)
    photo = Column(String, nullable=True) # File path
    ghana_card = Column(String, nullable=True)
    disability_status = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    guardians = relationship("Guardian", back_populates="student", cascade="all, delete-orphan")
    medical = relationship("StudentMedical", back_populates="student", uselist=False, cascade="all, delete-orphan")
    account = relationship("StudentAccount", back_populates="student", uselist=False, cascade="all, delete-orphan")
    admissions = relationship("Admission", back_populates="student")

    @property
    def current_class(self) -> str:
        # Get latest approved admission
        if not self.admissions: return "N/A"
        latest_adm = next((a for a in sorted(self.admissions, key=lambda x: x.created_at, reverse=True) 
                          if a.status == "Approved"), None)
        return latest_adm.class_room.name if latest_adm else "N/A"

    @property
    def class_id(self) -> Optional[int]:
        if not self.admissions: return None
        latest_adm = next((a for a in sorted(self.admissions, key=lambda x: x.created_at, reverse=True) 
                          if a.status == "Approved"), None)
        return latest_adm.class_id if latest_adm else None

    @property
    def stream_id(self) -> Optional[int]:
        if not self.admissions: return None
        latest_adm = next((a for a in sorted(self.admissions, key=lambda x: x.created_at, reverse=True) 
                          if a.status == "Approved"), None)
        return latest_adm.stream_id if latest_adm else None

    @property
    def current_stream(self) -> str:
        if not self.admissions: return "N/A"
        latest_adm = next((a for a in sorted(self.admissions, key=lambda x: x.created_at, reverse=True) 
                          if a.status == "Approved"), None)
        return latest_adm.stream.name if latest_adm and latest_adm.stream else "N/A"

    @property
    def status(self) -> str:
        if not self.admissions: return "Inactive"
        # Check if there's any approved admission
        has_approved = any(a.status == AdmissionStatus.Approved for a in self.admissions)
        if has_approved:
            return "Active"
        # Check for pending
        if any(a.status == AdmissionStatus.Pending for a in self.admissions):
            return "Pending Approval"
        return "Inactive"

    @property
    def pending_admission_id(self) -> Optional[int]:
        if not self.admissions: return None
        pending = next((a for a in self.admissions if a.status == AdmissionStatus.Pending), None)
        return pending.id if pending else None

    @property
    def admission_year(self) -> str:
        if not self.admissions: return "N/A"
        latest_adm = next((a for a in sorted(self.admissions, key=lambda x: x.created_at, reverse=True) 
                          if a.status == "Approved"), None)
        return latest_adm.academic_year_name if latest_adm else "N/A"

class Guardian(Base):
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    relationship_type = Column(String, nullable=False) # e.g. Father, Mother
    phone = Column(String, nullable=False)
    secondary_phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    address = Column(Text, nullable=False)
    occupation = Column(String, nullable=True)

    student = relationship("Student", back_populates="guardians")

class StudentMedical(Base):
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student.id", ondelete="CASCADE"), nullable=False)
    health_conditions = Column(Text, nullable=True)
    allergies = Column(Text, nullable=True)
    special_needs = Column(Text, nullable=True)

    student = relationship("Student", back_populates="medical")

class StudentAccount(Base):
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student.id", ondelete="CASCADE"), nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    must_change_password = Column(Boolean, default=True)
    is_active = Column(Boolean, default=False)

    student = relationship("Student", back_populates="account")
