import secrets
import string
import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.core.security import get_password_hash, verify_password
from .models import EVoucher, VoucherStatus, VoucherAttemptLog, VoucherAttemptResult
from .schemas import EVoucherCreate, EVoucherVerify, EVoucherSessionResponse

RESERVATION_TTL_MINUTES = 15

def generate_random_string(length: int, chars: str = string.digits) -> str:
    return ''.join(secrets.choice(chars) for _ in range(length))

class EVoucherService:
    @staticmethod
    def create_vouchers(db: Session, obj_in: EVoucherCreate) -> list:
        vouchers_data = []
        for _ in range(obj_in.count):
            voucher_number = generate_random_string(10) # 10 digit voucher
            pin = generate_random_string(6) # 6 digit PIN
            pin_hash = get_password_hash(pin)
            
            db_obj = EVoucher(
                voucher_number=voucher_number,
                pin_hash=pin_hash,
                academic_year_id=obj_in.academic_year_id,
                expires_at=obj_in.expires_at,
                status=VoucherStatus.Unused
            )
            db.add(db_obj)
            vouchers_data.append({"voucher_number": voucher_number, "pin": pin})
        
        db.commit()
        return vouchers_data

    @staticmethod
    def verify_voucher(db: Session, obj_in: EVoucherVerify, ip_address: str, user_agent: str) -> EVoucherSessionResponse:
        voucher = db.query(EVoucher).filter(EVoucher.voucher_number == obj_in.voucher_number).first()
        
        # Log attempt helper
        def log_attempt(result: VoucherAttemptResult):
            log = VoucherAttemptLog(
                voucher_number_entered=obj_in.voucher_number,
                ip_address=ip_address,
                user_agent=user_agent,
                result=result
            )
            db.add(log)
            db.commit()

        if not voucher:
            log_attempt(VoucherAttemptResult.NotFound)
            return EVoucherSessionResponse(valid=False, reason=VoucherAttemptResult.NotFound)

        if not verify_password(obj_in.pin, voucher.pin_hash):
            log_attempt(VoucherAttemptResult.InvalidPin)
            return EVoucherSessionResponse(valid=False, reason=VoucherAttemptResult.InvalidPin)

        if voucher.status == VoucherStatus.Used:
            log_attempt(VoucherAttemptResult.Used)
            return EVoucherSessionResponse(valid=False, reason=VoucherAttemptResult.Used)

        if voucher.status == VoucherStatus.Revoked:
            log_attempt(VoucherAttemptResult.NotFound) # Don't leak revoked status, just say not found/invalid
            return EVoucherSessionResponse(valid=False, reason=VoucherAttemptResult.NotFound)

        if voucher.expires_at < datetime.utcnow():
            voucher.status = VoucherStatus.Expired
            db.commit()
            log_attempt(VoucherAttemptResult.Expired)
            return EVoucherSessionResponse(valid=False, reason=VoucherAttemptResult.Expired)

        # Handle Reservation
        now = datetime.utcnow()
        # Even if currently RESERVED, if the correct PIN is provided (checked above),
        # we allow "taking over" the session. This prevents users from being locked out
        # if they refresh the page or clear their session.
        
        # All checks passed, Reserve it
        session_token = str(uuid.uuid4())
        voucher.status = VoucherStatus.Reserved
        voucher.reserved_at = now
        voucher.reserved_session_id = session_token
        db.commit()
        
        log_attempt(VoucherAttemptResult.Valid)
        return EVoucherSessionResponse(
            valid=True, 
            voucher_number=voucher.voucher_number,
            voucher_session_token=session_token,
            expires_at=now + timedelta(minutes=RESERVATION_TTL_MINUTES),
            academic_year_id=voucher.academic_year_id
        )

    @staticmethod
    def release_session(db: Session, session_token: str) -> bool:
        voucher = db.query(EVoucher).filter(EVoucher.reserved_session_id == session_token).first()
        if voucher and voucher.status == VoucherStatus.Reserved:
            voucher.status = VoucherStatus.Unused
            voucher.reserved_at = None
            voucher.reserved_session_id = None
            db.commit()
            return True
        return False

    @staticmethod
    def check_session(db: Session, session_token: str) -> EVoucherSessionResponse:
        voucher = db.query(EVoucher).filter(EVoucher.reserved_session_id == session_token).first()
        if not voucher or voucher.status != VoucherStatus.Reserved:
            return EVoucherSessionResponse(valid=False, reason=VoucherAttemptResult.NotFound)
        
        now = datetime.utcnow()
        expires_at = voucher.reserved_at + timedelta(minutes=RESERVATION_TTL_MINUTES)
        if expires_at < now:
            # Session expired
            voucher.status = VoucherStatus.Unused
            voucher.reserved_at = None
            voucher.reserved_session_id = None
            db.commit()
            return EVoucherSessionResponse(valid=False, reason=VoucherAttemptResult.Expired)
        
        return EVoucherSessionResponse(
            valid=True,
            voucher_number=voucher.voucher_number,
            voucher_session_token=session_token,
            expires_at=expires_at,
            academic_year_id=voucher.academic_year_id
        )
            
    @staticmethod
    def cleanup_expired_reservations(db: Session) -> int:
        now = datetime.utcnow()
        expired_time = now - timedelta(minutes=RESERVATION_TTL_MINUTES)
        
        expired_vouchers = db.query(EVoucher).filter(
            EVoucher.status == VoucherStatus.Reserved,
            EVoucher.reserved_at < expired_time
        ).all()
        
        count = len(expired_vouchers)
        for v in expired_vouchers:
            v.status = VoucherStatus.Unused
            v.reserved_at = None
            v.reserved_session_id = None
            
        db.commit()
        return count
