from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, selectinload, aliased
from typing import List, Optional
from app.db.session import get_db
from . import schemas, service, models
from .models import Admission, AdmissionStatus
from app.modules.students.models import Student
from app.modules.evoucher.models import EVoucher
from datetime import datetime
import logging
import traceback
import sys

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", response_model=schemas.AdmissionResponse)
def create_admission(
    obj_in: schemas.AdmissionWizardSubmit,
    db: Session = Depends(get_db)
):
    """
    Step 2-3 of Wizard: Capture all data and create a PENDING admission.
    """
    try:
        return service.AdmissionsService.create_pending_admission(
            db,
            voucher_session_token=obj_in.voucher_session_token,
            student_data=obj_in.student.model_dump(),
            guardian_data=[g.model_dump() for g in obj_in.guardians],
            medical_data=obj_in.medical.model_dump() if obj_in.medical else None,
            placement_data=obj_in.placement
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to create pending admission")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{admission_id}/approve", response_model=schemas.AdmissionResponse)
def approve_admission(
    admission_id: int,
    admin_id: int = 1, # TODO: Get from auth token
    db: Session = Depends(get_db)
):
    """
    Step 4 of Wizard (Admin Action): Official Approval.
    """
    try:
        return service.AdmissionsService.approve_admission(db, admission_id, admin_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to approve admission {admission_id}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[schemas.AdmissionResponse])
def list_admissions(
    status: Optional[str] = Query(None),
    class_id: int = Query(None),
    academic_year_id: int = Query(None),
    term_id: int = Query(None),
    search: str = Query(None),
    db: Session = Depends(get_db)
):
    try:
        # Using an alias 'adm' and selectinload is the SAFEST way to avoid 
        # AmbiguousColumn errors when filtering by common names like 'status'
        adm = aliased(Admission, name='adm')
        
        query = db.query(adm).options(
            selectinload(adm.student),
            selectinload(adm.voucher),
            selectinload(adm.class_room),
            selectinload(adm.academic_year),
            selectinload(adm.term),
            selectinload(adm.stream)
        )
        
        if status:
            try:
                # Handle case-insensitive status. Frontend sends 'Rejected', but DB now requires 'REJECTED'.
                # We convert input to uppercase to match the AdmissionStatus Enum members.
                status_upper = status.upper()
                enum_status = AdmissionStatus(status_upper)
                query = query.filter(adm.status == enum_status)
            except ValueError:
                # Invalid status string provided (not in PENDING, APPROVED, REJECTED)
                return []
            
        if class_id:
            query = query.filter(adm.class_id == class_id)
        if academic_year_id:
            query = query.filter(adm.academic_year_id == academic_year_id)
        if term_id:
            query = query.filter(adm.term_id == term_id)
        
        if search:
            search_filter = f"%{search}%"
            # Join required for filtering by student name or voucher number
            query = query.join(adm.student).join(adm.voucher).filter(
                (Student.first_name.ilike(search_filter)) |
                (Student.last_name.ilike(search_filter)) |
                (EVoucher.voucher_number.ilike(search_filter))
            )
        
        return query.order_by(adm.created_at.desc()).all()
    except Exception as e:
        logger.exception("Failed to list admissions")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{admission_id}/reject", response_model=schemas.AdmissionResponse)
def reject_admission(
    admission_id: int,
    admin_id: int = 1, # TODO: Get from auth token
    db: Session = Depends(get_db)
):
    """
    Reject admission application.
    """
    try:
        return service.AdmissionsService.reject_admission(db, admission_id, admin_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to reject admission {admission_id}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{admission_id}", response_model=schemas.AdmissionResponse)
def get_admission(
    admission_id: int,
    db: Session = Depends(get_db)
):
    try:
        admission = db.query(Admission).filter(Admission.id == admission_id).first()
        if not admission:
            raise HTTPException(status_code=404, detail="Admission not found")
        return admission
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to get admission {admission_id}")
        raise HTTPException(status_code=500, detail=str(e))
