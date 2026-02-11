from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from .models import VoucherStatus, VoucherAttemptResult

class EVoucherBase(BaseModel):
    voucher_number: str
    academic_year_id: int
    expires_at: datetime

class EVoucherCreate(BaseModel):
    academic_year_id: int
    count: int = Field(..., gt=0, le=1000) # max 1000 vouchers at once
    expires_at: datetime

class EVoucherResponse(EVoucherBase):
    id: int
    status: VoucherStatus
    reserved_at: Optional[datetime] = None
    used_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class EVoucherVerify(BaseModel):
    voucher_number: str
    pin: str

class EVoucherSessionResponse(BaseModel):
    valid: bool
    voucher_number: Optional[str] = None
    voucher_session_token: Optional[str] = None
    reason: Optional[VoucherAttemptResult] = None
    expires_at: Optional[datetime] = None
    academic_year_id: Optional[int] = None

class VoucherSessionCheck(BaseModel):
    voucher_session_token: str

class VoucherActionResponse(BaseModel):
    message: str
    success: bool

class PaginatedEVoucherResponse(BaseModel):
    items: List[EVoucherResponse]
    total: int
    page: int
    size: int
