from sqlalchemy import Column, Integer, String, JSON
from app.db.base_class import Base

class School(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    domain = Column(String, unique=True, index=True)
    settings = Column(JSON, default={})
