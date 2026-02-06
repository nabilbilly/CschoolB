from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date
import logging
from app.db.session import get_db
from . import schemas, models
from app.modules.evoucher.models import EVoucher

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", response_model=schemas.AcademicYearResponse)
def create_academic_year(
    obj_in: schemas.AcademicYearCreate,
    db: Session = Depends(get_db)
):
    try:
        # Check if name already exists
        existing = db.query(models.AcademicYear).filter(models.AcademicYear.name == obj_in.name).first()
        if existing:
            raise HTTPException(status_code=400, detail="Academic year name already exists")
        
        db_obj = models.AcademicYear(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to create academic year")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[schemas.AcademicYearResponse])
def list_academic_years(
    db: Session = Depends(get_db)
):
    try:
        return db.query(models.AcademicYear).all()
    except Exception as e:
        logger.exception("Failed to list academic years")
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{year_id}", response_model=schemas.AcademicYearResponse)
def update_academic_year(
    year_id: int,
    obj_in: schemas.AcademicYearUpdate,
    db: Session = Depends(get_db)
):
    try:
        year = db.query(models.AcademicYear).filter(models.AcademicYear.id == year_id).first()
        if not year:
            raise HTTPException(status_code=404, detail="Year not found")
        
        # Update fields
        if obj_in.name is not None:
            year.name = obj_in.name
        if obj_in.start_date is not None:
            year.start_date = obj_in.start_date
        if obj_in.end_date is not None:
            year.end_date = obj_in.end_date
        
        # Handle status change logic
        if obj_in.status is not None:
            if obj_in.status == models.YearStatus.ACTIVE:
                # Validate dates
                start = obj_in.start_date if obj_in.start_date is not None else year.start_date
                end = obj_in.end_date if obj_in.end_date is not None else year.end_date
                
                if not start or not end:
                    raise HTTPException(status_code=400, detail="Start date and end date are required to activate academic year")
                if start >= end:
                    raise HTTPException(status_code=400, detail="Start date must be before end date")
                
                # Check for other active years
                active_year = db.query(models.AcademicYear).filter(
                    models.AcademicYear.status == models.YearStatus.ACTIVE,
                    models.AcademicYear.id != year_id
                ).first()
                if active_year:
                    raise HTTPException(status_code=400, detail="Another academic year is already active")
            
            year.status = obj_in.status

        db.commit()
        db.refresh(year)
        return year
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to update academic year {year_id}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{year_id}")
def delete_academic_year(
    year_id: int,
    db: Session = Depends(get_db)
):
    try:
        year = db.query(models.AcademicYear).filter(models.AcademicYear.id == year_id).first()
        if not year:
            raise HTTPException(status_code=404, detail="Year not found")
        
        # Safety Check: Prevent deleting active year
        if year.status == models.YearStatus.ACTIVE:
            raise HTTPException(status_code=400, detail="Cannot delete an Active academic year. Archive it first.")
        
        # Dependency Check: Check for associated vouchers
        vouchers = db.query(EVoucher).filter(EVoucher.academic_year_id == year_id).first()
        if vouchers:
            raise HTTPException(status_code=400, detail="Cannot delete academic year: Associated vouchers exist.")
        
        db.delete(year)
        db.commit()
        return {"message": "Academic year deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to delete academic year {year_id}")
        raise HTTPException(status_code=500, detail=str(e))

# --- Term Endpoints ---

def validate_term_dates(db: Session, term: models.Term, year: models.AcademicYear, new_start: date = None, new_end: date = None, result_open: date = None, result_close: date = None):
    start = new_start or term.start_date
    end = new_end or term.end_date
    r_open = result_open or term.result_open_date
    r_close = result_close or term.result_close_date

    if start and end:
        if start >= end:
            raise HTTPException(status_code=400, detail="Term start date must be before end date")
        
        # Boundary check
        if year.start_date and start < year.start_date:
            raise HTTPException(status_code=400, detail=f"Term start date cannot be before academic year start date ({year.start_date})")
        if year.end_date and end > year.end_date:
            raise HTTPException(status_code=400, detail=f"Term end date cannot be after academic year end date ({year.end_date})")

        # Overlap check
        overlap = db.query(models.Term).filter(
            models.Term.academic_year_id == year.id,
            models.Term.id != term.id,
            models.Term.start_date < end,
            models.Term.end_date > start
        ).first()
        if overlap:
            raise HTTPException(status_code=400, detail=f"Term dates overlap with existing term: {overlap.name}")

    # Result window check
    if r_open or r_close:
        if not (start and end):
            raise HTTPException(status_code=400, detail="Term start and end dates must be set before defining result windows")
        if r_open and (r_open < start or r_open > end):
            raise HTTPException(status_code=400, detail="Result open date must be within term boundaries")
        if r_close and (r_close < start or r_close > end):
            raise HTTPException(status_code=400, detail="Result close date must be within term boundaries")
        if r_open and r_close and r_open > r_close:
            raise HTTPException(status_code=400, detail="Result open date must be before close date")

@router.post("/{year_id}/terms", response_model=schemas.TermResponse)
def create_term(
    year_id: int,
    obj_in: schemas.TermCreate,
    db: Session = Depends(get_db)
):
    year = db.query(models.AcademicYear).filter(models.AcademicYear.id == year_id).first()
    if not year:
        raise HTTPException(status_code=404, detail="Academic year not found")
    
    db_obj = models.Term(**obj_in.dict(), academic_year_id=year_id)
    
    # If not draft, validate immediately
    if db_obj.status != models.TermStatus.DRAFT:
        if not db_obj.start_date or not db_obj.end_date:
            raise HTTPException(status_code=400, detail="Start and end dates are required for non-draft terms")
        validate_term_dates(db, db_obj, year)
        
        if db_obj.status == models.TermStatus.ACTIVE:
            active_term = db.query(models.Term).filter(
                models.Term.academic_year_id == year_id,
                models.Term.status == models.TermStatus.ACTIVE
            ).first()
            if active_term:
                raise HTTPException(status_code=400, detail="Another term is already active in this academic year")

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.get("/{year_id}/terms", response_model=List[schemas.TermResponse])
def list_terms(
    year_id: int,
    db: Session = Depends(get_db)
):
    try:
        return db.query(models.Term).filter(models.Term.academic_year_id == year_id).order_by(models.Term.sequence).all()
    except Exception as e:
        logger.exception(f"Failed to list terms for year {year_id}")
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/terms/{term_id}", response_model=schemas.TermResponse)
def update_term(
    term_id: int,
    obj_in: schemas.TermUpdate,
    db: Session = Depends(get_db)
):
    try:
        term = db.query(models.Term).filter(models.Term.id == term_id).first()
        if not term:
            raise HTTPException(status_code=404, detail="Term not found")
        
        year = term.academic_year
        
        update_data = obj_in.dict(exclude_unset=True)
        
        # If activating, perform checks
        new_status = update_data.get("status")
        if new_status == models.TermStatus.ACTIVE:
            if year.status != models.YearStatus.ACTIVE:
                raise HTTPException(status_code=400, detail="Cannot activate a term in a non-active academic year")
            
            active_term = db.query(models.Term).filter(
                models.Term.academic_year_id == year.id,
                models.Term.status == models.TermStatus.ACTIVE,
                models.Term.id != term_id
            ).first()
            if active_term:
                raise HTTPException(status_code=400, detail="Another term is already active in this academic year")

        # Validate dates if they are being updated or if status is changing to non-draft
        if any(k in update_data for k in ["start_date", "end_date", "result_open_date", "result_close_date"]) or \
           (new_status and new_status != models.TermStatus.DRAFT):
            
            # Preview updates for validation
            temp_start = update_data.get("start_date", term.start_date)
            temp_end = update_data.get("end_date", term.end_date)
            
            if (new_status or term.status) != models.TermStatus.DRAFT:
                if not temp_start or not temp_end:
                    raise HTTPException(status_code=400, detail="Start and end dates are required for non-draft terms")
            
            validate_term_dates(
                db, term, year,
                new_start=update_data.get("start_date"),
                new_end=update_data.get("end_date"),
                result_open=update_data.get("result_open_date"),
                result_close=update_data.get("result_close_date")
            )

        for field, value in update_data.items():
            setattr(term, field, value)
        
        db.commit()
        db.refresh(term)
        return term
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to update term {term_id}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/terms/{term_id}")
def delete_term(
    term_id: int,
    db: Session = Depends(get_db)
):
    try:
        term = db.query(models.Term).filter(models.Term.id == term_id).first()
        if not term:
            raise HTTPException(status_code=404, detail="Term not found")
        
        # TODO: Check for dependent records (results, attendance, etc.) once implemented
        
        db.delete(term)
        db.commit()
        return {"message": "Term deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to delete term {term_id}")
        raise HTTPException(status_code=500, detail=str(e))

# --- ClassRoom and Stream Endpoints ---

@router.post("/classes", response_model=schemas.ClassRoomResponse)
def create_class(
    obj_in: schemas.ClassRoomCreate,
    db: Session = Depends(get_db)
):
    try:
        db_obj = models.ClassRoom(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    except Exception as e:
        logger.exception("Failed to create class")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/classes", response_model=List[schemas.ClassRoomResponse])
def list_classes(
    db: Session = Depends(get_db)
):
    try:
        from sqlalchemy.orm import joinedload
        return db.query(models.ClassRoom).options(joinedload(models.ClassRoom.streams)).all()
    except Exception as e:
        logger.exception("Failed to list classes")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/streams", response_model=schemas.StreamResponse)
def create_stream(
    obj_in: schemas.StreamCreate,
    db: Session = Depends(get_db)
):
    try:
        db_obj = models.Stream(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    except Exception as e:
        logger.exception("Failed to create stream")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/classes/{class_id}/streams", response_model=List[schemas.StreamResponse])
def list_streams(
    class_id: int,
    db: Session = Depends(get_db)
):
    try:
        return db.query(models.Stream).filter(models.Stream.class_id == class_id).all()
    except Exception as e:
        logger.exception(f"Failed to list streams for class {class_id}")
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/classes/{class_id}", response_model=schemas.ClassRoomResponse)
def update_class(
    class_id: int,
    obj_in: schemas.ClassRoomUpdate,
    db: Session = Depends(get_db)
):
    try:
        db_obj = db.query(models.ClassRoom).filter(models.ClassRoom.id == class_id).first()
        if not db_obj:
            raise HTTPException(status_code=404, detail="Class not found")
        
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.commit()
        db.refresh(db_obj)
        return db_obj
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to update class {class_id}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/classes/{class_id}")
def delete_class(
    class_id: int,
    db: Session = Depends(get_db)
):
    try:
        db_obj = db.query(models.ClassRoom).filter(models.ClassRoom.id == class_id).first()
        if not db_obj:
            raise HTTPException(status_code=404, detail="Class not found")
        
        # Check for dependent admissions
        if db_obj.admissions:
            raise HTTPException(status_code=400, detail="Cannot delete class with existing admissions. Archive it instead.")
        
        db.delete(db_obj)
        db.commit()
        return {"message": "Class deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to delete class {class_id}")
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/streams/{stream_id}", response_model=schemas.StreamResponse)
def update_stream(
    stream_id: int,
    obj_in: schemas.StreamUpdate,
    db: Session = Depends(get_db)
):
    try:
        db_obj = db.query(models.Stream).filter(models.Stream.id == stream_id).first()
        if not db_obj:
            raise HTTPException(status_code=404, detail="Stream not found")
        
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.commit()
        db.refresh(db_obj)
        return db_obj
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to update stream {stream_id}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/streams/{stream_id}")
def delete_stream(
    stream_id: int,
    db: Session = Depends(get_db)
):
    try:
        db_obj = db.query(models.Stream).filter(models.Stream.id == stream_id).first()
        if not db_obj:
            raise HTTPException(status_code=404, detail="Stream not found")
        
        # Check for dependent admissions
        if db_obj.admissions:
            raise HTTPException(status_code=400, detail="Cannot delete stream with existing admissions.")
        
        db.delete(db_obj)
        db.commit()
        return {"message": "Stream deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Failed to delete stream {stream_id}")
        raise HTTPException(status_code=500, detail=str(e))
