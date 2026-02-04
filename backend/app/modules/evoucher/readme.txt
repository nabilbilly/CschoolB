Implementation Plan - Modular FastAPI Backend for cschool
The goal is to build a scalable, modular FastAPI backend for the cschool SaaS platform. The system will handle multiple schools (tenancy), user roles, and distinct functional modules like Students, Teachers, and Bursar, while sharing core infrastructure.

User Review Required
IMPORTANT

Database Selection: I will configure the project to use PostgreSQL as requested. Auth: I will implement JWT-based authentication.

Proposed Changes
Refined Directory Structure
I will organize the backend into core, 

db
, shared, and modules to ensure strict separation of concerns and scalability.

[NEW] 

app/api.py
Central hub for including all module routers.
[NEW] app/core/

security.py
: Auth helpers.

permissions.py
: RBAC logic.

tenancy.py
: Multi-school context.
[NEW] app/shared/
Cross-cutting models: 

user.py
, 

school.py
, 

role.py
.
[NEW] E-Voucher Module Implementation
Based on the provided contract, I will implement:

Models & Database (app/modules/evoucher/models.py & app/modules/academics/models.py)
AcademicYear: id, name, status.
EVoucher: id, voucher_number, pin_hash, academic_year_id, status (Unused/Reserved/Used/Expired/Revoked), reserved_at, reserved_session_id.
VoucherAttemptLog: Logging for verification attempts.
Service Logic (app/modules/evoucher/service.py)
Voucher generation with secure PIN hashing.
Verification logic with status checks and reservation (TTL handling).
Session management (Refresh/Release).
API Endpoints (app/modules/evoucher/router.py)
Admin: Create, List, Revoke.
Public: Verify, Check Session, Release Session.
Persistence Layer
Using PostgreSQL via SQLAlchemy.
Migrations managed by Alembic.
Verification Plan
Automated Tests
Unit tests for voucher verification logic.
Integration tests for reservation TTL.
Health check endpoint /health.