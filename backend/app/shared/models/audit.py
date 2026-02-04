from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from app.db.base_class import Base

class AuditLog(Base):
    id = Column(Integer, primary_key=True, index=True)
    entity = Column(String, index=True) # Admission, Voucher, etc.
    entity_id = Column(Integer, index=True)
    action = Column(String) # Verify, Approve, etc.
    admin_id = Column(Integer, nullable=True) # FK to user
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
