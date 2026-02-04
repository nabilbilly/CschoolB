from app.db.session import engine
from app.db.base import Base
# Import all models here so SQLAlchemy knows about them
from app.shared.models.school import School
from app.shared.models.user import User
from app.shared.models.role import Role
from app.modules.academics.models import AcademicYear
from app.modules.evoucher.models import EVoucher, VoucherAttemptLog

def init_db():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

if __name__ == "__main__":
    init_db()
