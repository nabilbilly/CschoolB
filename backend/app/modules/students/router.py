from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from fastapi.security import OAuth2PasswordBearer
from . import schemas, models
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.config import settings
from jose import jwt, JWTError

router = APIRouter()

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/students/login"
)

def get_current_student(
    db: Session = Depends(get_db),
    token: str = Depends(reusable_oauth2)
) -> models.Student:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    
    student = db.query(models.Student).filter(
        models.Student.account.has(username=username)
    ).first()
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@router.post("/login", response_model=schemas.Token)
def student_login(
    obj_in: schemas.StudentLogin,
    db: Session = Depends(get_db)
):
    # Search by index_number OR username
    student = db.query(models.Student).filter(
        (models.Student.index_number == obj_in.username) |
        (models.Student.account.has(username=obj_in.username))
    ).first()

    if not student or not student.account:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not student.account.is_active:
        raise HTTPException(status_code=401, detail="Account is inactive. Please contact admin.")

    if not verify_password(obj_in.password, student.account.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(
        data={"sub": student.account.username, "id": student.id, "type": "student"}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "must_change_password": student.account.must_change_password,
        "student_name": f"{student.first_name} {student.last_name}",
        "index_number": student.index_number or "N/A"
    }

@router.post("/change-password")
def change_password(
    obj_in: schemas.StudentPasswordChange,
    current_student: models.Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    if not verify_password(obj_in.current_password, current_student.account.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect current password")
    
    current_student.account.hashed_password = get_password_hash(obj_in.new_password)
    current_student.account.must_change_password = False
    
    db.commit()
    return {"message": "Password changed successfully", "success": True}

@router.get("/me/profile", response_model=schemas.StudentResponse)
def get_my_profile(
    current_student: models.Student = Depends(get_current_student)
):
    return current_student

@router.patch("/me/profile", response_model=schemas.StudentResponse)
def update_my_profile(
    obj_in: schemas.StudentUpdate,
    current_student: models.Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    update_data = obj_in.model_dump(exclude_unset=True)
    
    # Students can only update certain fields themselves (e.g., photo)
    # For now, let's allow photo and maybe address/city if we wanted to
    # But the request specifically mentioned photos.
    
    allowed_fields = {"photo", "address", "city"}
    sanitized_data = {k: v for k, v in update_data.items() if k in allowed_fields}
    
    for field, value in sanitized_data.items():
        setattr(current_student, field, value)
    
    db.commit()
    db.refresh(current_student)
    return current_student

@router.get("/", response_model=List[schemas.StudentResponse])
def list_students(
    search: Optional[str] = None,
    status: Optional[str] = None,
    academic_year_id: Optional[int] = None,
    class_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    from sqlalchemy.orm import joinedload
    from app.modules.admissions.models import Admission, AdmissionStatus
    
    query = db.query(models.Student).options(
        joinedload(models.Student.admissions).joinedload(Admission.class_room),
        joinedload(models.Student.admissions).joinedload(Admission.academic_year),
        joinedload(models.Student.admissions).joinedload(Admission.stream)
    )

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (models.Student.first_name.ilike(search_filter)) |
            (models.Student.last_name.ilike(search_filter)) |
            (models.Student.index_number.ilike(search_filter))
        )

    # Note: Status, Academic Year, and Class filtering requires joining with Admissions
    if any([status, academic_year_id, class_id]):
        query = query.join(models.Student.admissions)
        
        if status:
            if status == "Active":
                query = query.filter(Admission.status == AdmissionStatus.APPROVED)
            elif status == "Pending Approval":
                query = query.filter(Admission.status == AdmissionStatus.PENDING)
        
        if academic_year_id:
            query = query.filter(Admission.academic_year_id == academic_year_id)
        
        if class_id:
            query = query.filter(Admission.class_id == class_id)

    return query.all()

@router.get("/{student_id}", response_model=schemas.StudentResponse)
def get_student(
    student_id: int,
    db: Session = Depends(get_db)
):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@router.patch("/{student_id}", response_model=schemas.StudentResponse)
def update_student(
    student_id: int,
    obj_in: schemas.StudentUpdate,
    db: Session = Depends(get_db)
):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    update_data = obj_in.model_dump(exclude_unset=True)
    
    # Handle Enrollment Updates
    class_id = update_data.pop("class_id", None)
    stream_id = update_data.pop("stream_id", None)
    
    if class_id is not None or stream_id is not None:
        from app.modules.admissions.models import Admission, AdmissionStatus
        latest_adm = db.query(Admission).filter(
            Admission.student_id == student_id,
            Admission.status == AdmissionStatus.APPROVED
        ).order_by(Admission.created_at.desc()).first()
        
        if latest_adm:
            if class_id is not None:
                latest_adm.class_id = class_id
            if stream_id is not None:
                latest_adm.stream_id = stream_id
            db.add(latest_adm)

    for field, value in update_data.items():
        setattr(student, field, value)
    
    db.commit()
    db.refresh(student)
    return student

@router.post("/{student_id}/reset-password")
def reset_student_password(
    student_id: int,
    obj_in: schemas.StudentPasswordChange, # Re-using this schema as it has new_password (even if current_password is not needed)
    db: Session = Depends(get_db)
):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student or not student.account:
        raise HTTPException(status_code=404, detail="Student account not found")
    
    student.account.hashed_password = get_password_hash(obj_in.new_password)
    student.account.must_change_password = True
    
    db.commit()
    return {"message": "Password reset successfully", "success": True}
