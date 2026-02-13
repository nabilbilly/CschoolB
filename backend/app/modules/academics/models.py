from sqlalchemy import Column, Integer, String, Date, Enum as SqlEnum, ForeignKey, Index
from sqlalchemy.orm import relationship
import enum
from app.db.base_class import Base

class YearStatus(str, enum.Enum):
    ACTIVE = "Active"
    DRAFT = "Draft"
    ARCHIVED = "Archived"

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            for member in cls:
                if member.value.upper() == value.upper():
                    return member
        return None

class TermStatus(str, enum.Enum):
    DRAFT = "Draft"
    ACTIVE = "Active"
    CLOSED = "Closed"

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            for member in cls:
                if member.value.upper() == value.upper():
                    return member
        return None

class AcademicYear(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True) # e.g., 2026/2027
    status = Column(SqlEnum(YearStatus, values_callable=lambda x: [e.value for e in x]), default=YearStatus.DRAFT)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)

    terms = relationship("Term", back_populates="academic_year", cascade="all, delete-orphan", passive_deletes=True)

class Term(Base):
    id = Column(Integer, primary_key=True, index=True)
    academic_year_id = Column(Integer, ForeignKey("academicyear.id", ondelete="RESTRICT"), nullable=False)
    name = Column(String, nullable=False) # e.g., Term 1
    status = Column(SqlEnum(TermStatus, values_callable=lambda x: [e.value for e in x]), default=TermStatus.DRAFT)
    sequence = Column(Integer, default=1)
    
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    
    result_open_date = Column(Date, nullable=True)
    result_close_date = Column(Date, nullable=True)

    academic_year = relationship("AcademicYear", back_populates="terms")

    __table_args__ = (
        Index("ix_term_academic_year_id_start_date", "academic_year_id", "start_date"),
    )

class ClassRoom(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True) # e.g. JHS 1, Primary 1
    level = Column(String, nullable=False) # e.g. JHS, Primary
    
    admissions = relationship("Admission", back_populates="class_room")
    streams = relationship("Stream", back_populates="class_room")

class Stream(Base):
    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classroom.id"), nullable=False)
    name = Column(String, nullable=False) # e.g. A, B, Gold, Blue
    
    class_room = relationship("ClassRoom", back_populates="streams")
    admissions = relationship("Admission", back_populates="stream")
