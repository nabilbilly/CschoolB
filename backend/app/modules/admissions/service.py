from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException
import secrets
import string

from .models import Admission, AdmissionStatus
from ..evoucher.models import EVoucher, VoucherStatus
from ..students.models import Student, Guardian, StudentMedical, StudentAccount, Gender
from ..academics.models import AcademicYear, ClassRoom, Stream
from app.shared.models.audit import AuditLog
from app.core.security import get_password_hash
import traceback
import sys

class AdmissionsService:
    @staticmethod
    def create_pending_admission(
        db: Session,
        voucher_session_token: str,
        student_data: dict,
        guardian_data: List[dict],
        medical_data: Optional[dict],
        placement_data: dict
    ) -> Admission:
        # 1. Validate Voucher Session
        voucher = db.query(EVoucher).filter(EVoucher.reserved_session_id == voucher_session_token).first()
        if not voucher or voucher.status != VoucherStatus.RESERVED:
            raise HTTPException(status_code=400, detail="Invalid or expired voucher session")
        
        # 2. Check if voucher matches academic year
        if voucher.academic_year_id != placement_data['academic_year_id']:
            raise HTTPException(status_code=400, detail="Academic year mismatch for this voucher")

        try:
            # 3. Create Student
            student = Student(
                first_name=student_data['first_name'],
                middle_name=student_data.get('middle_name'),
                last_name=student_data['last_name'],
                gender=student_data['gender'],
                date_of_birth=student_data['date_of_birth'],
                nationality=student_data['nationality'],
                address=student_data.get('address'),
                city=student_data.get('city'),
                photo=student_data.get('photo')
            )
            db.add(student)
            db.flush() # Get student ID

            # 4. Create Guardians
            for g in guardian_data:
                guardian = Guardian(
                    student_id=student.id,
                    name=g['name'],
                    relationship_type=g['relationship_type'],
                    phone=g['phone'],
                    secondary_phone=g.get('secondary_phone'),
                    email=g.get('email'),
                    address=g['address'],
                    occupation=g.get('occupation')
                )
                db.add(guardian)

            # 5. Create Medical (Optional)
            if medical_data:
                medical = StudentMedical(
                    student_id=student.id,
                    health_conditions=medical_data.get('health_conditions'),
                    allergies=medical_data.get('allergies'),
                    special_needs=medical_data.get('special_needs')
                )
                db.add(medical)

            # 6. Create Student Account (Inactive)
            # Generate temporary password
            temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
            username = f"std_{student.id}_{secrets.choice(string.digits)}{secrets.choice(string.digits)}" # Basic username for now
            
            account = StudentAccount(
                student_id=student.id,
                username=username,
                hashed_password=get_password_hash(temp_password),
                must_change_password=True,
                is_active=False
            )
            db.add(account)

            # 7. Create Admission (Pending)
            admission = Admission(
                student_id=student.id,
                academic_year_id=placement_data['academic_year_id'],
                class_id=placement_data['class_id'],
                stream_id=placement_data.get('stream_id'),
                term_id=placement_data['term_id'],
                voucher_id=voucher.id,
                status=AdmissionStatus.PENDING
            )
            db.add(admission)
            db.flush()

            # 8. Log Action
            audit = AuditLog(
                entity="Admission",
                entity_id=admission.id,
                action="CREATE_PENDING",
                notes=f"Pending admission created using voucher {voucher.voucher_number}"
            )
            db.add(audit)

            db.commit()
            db.refresh(admission)
            
            # Attach temp_password for UI display (response schema)
            setattr(admission, 'temp_password', temp_password)
            
            return admission

        except Exception as e:
            db.rollback()
            print(f"DEBUG: Admission creation failed: {e}", file=sys.stderr)
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Failed to create admission: {str(e)}")

    @staticmethod
    def approve_admission(db: Session, admission_id: int, admin_id: int) -> Admission:
        admission = db.query(Admission).filter(Admission.id == admission_id).first()
        if not admission:
            raise HTTPException(status_code=404, detail="Admission record not found")
        
        if admission.status not in [AdmissionStatus.PENDING, AdmissionStatus.REJECTED]:
            raise HTTPException(status_code=400, detail="Admission is already processed (Approved)")

        try:
            # 1. Update Admission status
            admission.status = AdmissionStatus.APPROVED
            admission.approved_by_admin_id = admin_id
            admission.approved_at = datetime.utcnow()

            # 2. Mark Voucher as Used
            voucher = admission.voucher
            voucher.status = VoucherStatus.USED
            voucher.used_at = datetime.utcnow()
            voucher.used_by_student_id = admission.student_id

            # 3. Activate Student Account
            if admission.student.account:
                admission.student.account.is_active = True

            # 4. Generate Index Number (Format: SCH/{LEVEL}/{YEAR}/{SEQ})
            # LEVEL: From ClassRoom
            # YEAR: From AcademicYear (name part, e.g., 2026)
            level_code = admission.class_room.level[:3].upper() # JHS or PRI
            year_short = admission.academic_year.name.split('/')[0][-2:] # 26
            
            # Simple sequence based on count in same year/level
            seq_count = db.query(Student).join(Admission).filter(
                Admission.academic_year_id == admission.academic_year_id,
                Admission.status == AdmissionStatus.APPROVED
            ).count()
            
            index_number = f"SCH/{level_code}/{year_short}/{seq_count + 1:04d}"
            admission.student.index_number = index_number

            # 5. Log Action
            audit = AuditLog(
                entity="Admission",
                entity_id=admission.id,
                action="APPROVE",
                admin_id=admin_id,
                notes=f"Admission approved. Generated index: {index_number}"
            )
            db.add(audit)

            db.commit()
            db.refresh(admission)
            return admission

        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to approve admission: {str(e)}")

    @staticmethod
    def reject_admission(db: Session, admission_id: int, admin_id: int) -> Admission:
        admission = db.query(Admission).filter(Admission.id == admission_id).first()
        if not admission:
            raise HTTPException(status_code=404, detail="Admission record not found")
        
        if admission.status != AdmissionStatus.PENDING:
            raise HTTPException(status_code=400, detail="Admission is already processed")

        try:
            # 1. Update Admission status
            admission.status = AdmissionStatus.REJECTED
            
            # 2. Reset Voucher (Optional: or mark as invalid)
            # For now, let's make the voucher reusable if rejected?
            # User said "voucher marked used or invalid based on policy"
            # Let's mark it as UNUSED so the user can try again or someone else can.
            voucher = admission.voucher
            if voucher:
                voucher.status = VoucherStatus.UNUSED
                voucher.reserved_at = None
                voucher.reserved_session_id = None

            # 3. Log Action
            audit = AuditLog(
                entity="Admission",
                entity_id=admission.id,
                action="REJECT",
                admin_id=admin_id,
                notes=f"Admission rejected by admin {admin_id}."
            )
            db.add(audit)

            db.commit()
            db.refresh(admission)
            return admission

        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to reject admission: {str(e)}")
