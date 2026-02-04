from pydantic import BaseModel
from datetime import date
from typing import Optional, List
from .models import YearStatus, TermStatus

class AcademicYearBase(BaseModel):
    name: str
    status: YearStatus
    start_date: date | None = None
    end_date: date | None = None

class AcademicYearCreate(AcademicYearBase):
    pass

class AcademicYearUpdate(BaseModel):
    name: str | None = None
    status: YearStatus | None = None
    start_date: date | None = None
    end_date: date | None = None

class TermBase(BaseModel):
    name: str
    status: TermStatus = TermStatus.DRAFT
    sequence: int = 1
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    result_open_date: Optional[date] = None
    result_close_date: Optional[date] = None

class TermCreate(TermBase):
    pass

class TermUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[TermStatus] = None
    sequence: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    result_open_date: Optional[date] = None
    result_close_date: Optional[date] = None

class TermResponse(TermBase):
    id: int
    academic_year_id: int

    class Config:
        from_attributes = True

class AcademicYearResponse(AcademicYearBase):
    id: int
    terms: List[TermResponse] = []

    class Config:
        from_attributes = True

class StreamBase(BaseModel):
    name: str

class StreamCreate(StreamBase):
    class_id: int

class StreamUpdate(BaseModel):
    name: Optional[str] = None
    class_id: Optional[int] = None

class StreamResponse(StreamBase):
    id: int
    class_id: int

    class Config:
        from_attributes = True

class ClassRoomBase(BaseModel):
    name: str
    level: str

class ClassRoomCreate(ClassRoomBase):
    pass

class ClassRoomUpdate(BaseModel):
    name: Optional[str] = None
    level: Optional[str] = None

class ClassRoomResponse(ClassRoomBase):
    id: int
    streams: List[StreamResponse] = []

    class Config:
        from_attributes = True
