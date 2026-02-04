from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from app.db.base_class import Base

class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)
    role_id = Column(Integer, ForeignKey("role.id"))
    school_id = Column(Integer, ForeignKey("school.id"))
