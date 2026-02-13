from sqlalchemy import Column, Integer, String, Enum as SqlEnum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
import enum
from typing import Optional
from datetime import datetime
from app.db.base_class import Base

class AdmissionStatus(str, enum.Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            for member in cls:
                if member.value.upper() == value.upper():
                    return member
        return None

class Admission(Base):
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student.id"), nullable=False)
    academic_year_id = Column(Integer, ForeignKey("academicyear.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classroom.id"), nullable=False)
    stream_id = Column(Integer, ForeignKey("stream.id"), nullable=True)
    term_id = Column(Integer, ForeignKey("term.id"), nullable=False)
    voucher_id = Column(Integer, ForeignKey("evoucher.id"), nullable=False)
    
    status = Column(SqlEnum(AdmissionStatus, values_callable=lambda x: [e.value for e in x]), default=AdmissionStatus.PENDING)
    approved_by_admin_id = Column(Integer, nullable=True) # FK to user
    approved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="admissions")
    academic_year = relationship("AcademicYear")
    class_room = relationship("ClassRoom", back_populates="admissions")
    stream = relationship("Stream", back_populates="admissions")
    term = relationship("Term")
    voucher = relationship("EVoucher")

    @property
    def student_name(self) -> str:
        if self.student:
            parts = [self.student.first_name]
            if self.student.middle_name:
                parts.append(self.student.middle_name)
            parts.append(self.student.last_name)
            return " ".join(parts)
        return "Unknown"

    @property
    def voucher_number(self) -> str:
        return self.voucher.voucher_number if self.voucher else "N/A"

    @property
    def class_name(self) -> str:
        name = self.class_room.name if self.class_room else "N/A"
        if self.stream:
            name += f" ({self.stream.name})"
        return name

    @property
    def academic_year_name(self) -> str:
        return self.academic_year.name if self.academic_year else "N/A"

    @property
    def term_name(self) -> str:
        return self.term.name if self.term else "N/A"

    @property
    def student_index_number(self) -> Optional[str]:
        return self.student.index_number if self.student else None
