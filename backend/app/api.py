from fastapi import APIRouter
from app.modules.evoucher.router import router as evoucher_router
from app.modules.academics.router import router as academics_router
from app.modules.admissions.router import router as admissions_router
from app.modules.students.router import router as students_router
from app.modules.fees.router import router as fees_router
from app.modules.notices.router import router as notices_router
from app.modules.results.router import router as results_router
from app.modules.staff.router import router as staff_router
from app.modules.teachers.router import router as teachers_router
from app.modules.timetable.router import router as timetable_router
from app.modules.media.router import router as media_router

api_router = APIRouter()

api_router.include_router(evoucher_router, prefix="/evoucher", tags=["evoucher"])
api_router.include_router(academics_router, prefix="/academics", tags=["academics"])
api_router.include_router(admissions_router, prefix="/admissions", tags=["admissions"])
api_router.include_router(students_router, prefix="/students", tags=["students"])
api_router.include_router(fees_router, prefix="/fees", tags=["fees"])
api_router.include_router(notices_router, prefix="/notices", tags=["notices"])
api_router.include_router(results_router, prefix="/results", tags=["results"])
api_router.include_router(staff_router, prefix="/staff", tags=["staff"])
api_router.include_router(teachers_router, prefix="/teachers", tags=["teachers"])
api_router.include_router(timetable_router, prefix="/timetable", tags=["timetable"])
api_router.include_router(media_router, prefix="/media", tags=["media"])
