from fastapi import APIRouter
from app.modules.evoucher.router import router as evoucher_router
from app.modules.academics.router import router as academics_router
from app.modules.admissions.router import router as admissions_router
from app.modules.students.router import router as students_router

api_router = APIRouter()

api_router.include_router(evoucher_router, prefix="/evoucher", tags=["evoucher"])
api_router.include_router(academics_router, prefix="/academics", tags=["academics"])
api_router.include_router(admissions_router, prefix="/admissions", tags=["admissions"])
api_router.include_router(students_router, prefix="/students", tags=["students"])
