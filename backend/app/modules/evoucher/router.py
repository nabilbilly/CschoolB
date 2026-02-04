from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from . import schemas, service, models

router = APIRouter()

# --- Public Endpoints ---

@router.post("/verify", response_model=schemas.EVoucherSessionResponse)
def verify_voucher(
    obj_in: schemas.EVoucherVerify, 
    request: Request,
    db: Session = Depends(get_db)
):
    ip_address = request.client.host
    user_agent = request.headers.get("user-agent", "unknown")
    return service.EVoucherService.verify_voucher(db, obj_in, ip_address, user_agent)

@router.get("/check-session/{session_token}", response_model=schemas.EVoucherSessionResponse)
def check_session(
    session_token: str,
    db: Session = Depends(get_db)
):
    return service.EVoucherService.check_session(db, session_token)

@router.delete("/release-session/{session_token}", response_model=schemas.VoucherActionResponse)
def release_session(
    session_token: str,
    db: Session = Depends(get_db)
):
    success = service.EVoucherService.release_session(db, session_token)
    if success:
        return {"message": "Session released successfully", "success": True}
    raise HTTPException(status_code=404, detail="Session not found or already released")

# --- Admin Endpoints (Skeletons - will add auth later) ---

@router.post("/admin/vouchers", response_model=List[dict])
def create_vouchers(
    obj_in: schemas.EVoucherCreate,
    db: Session = Depends(get_db)
):
    # TODO: Add admin permission check
    return service.EVoucherService.create_vouchers(db, obj_in)

@router.get("/admin/vouchers", response_model=schemas.PaginatedEVoucherResponse)
def list_vouchers(
    academic_year_id: int = None,
    status: models.VoucherStatus = None,
    page: int = 1,
    size: int = 50,
    db: Session = Depends(get_db)
):
    # TODO: Add admin permission check
    query = db.query(models.EVoucher)
    if academic_year_id:
        query = query.filter(models.EVoucher.academic_year_id == academic_year_id)
    if status:
        query = query.filter(models.EVoucher.status == status)
    
    total = query.count()
    skip = (page - 1) * size
    items = query.offset(skip).limit(size).all()

    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size
    }

@router.delete("/admin/cleanup-reservations", response_model=schemas.VoucherActionResponse)
def cleanup_expired_reservations(
    db: Session = Depends(get_db)
):
    # TODO: Add admin permission check
    count = service.EVoucherService.cleanup_expired_reservations(db)
    return {"message": f"Cleaned up {count} expired reservations", "success": True}
