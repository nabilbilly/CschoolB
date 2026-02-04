Academic Year Management Updates
Goal Description
Enhance 
AcademicYear
 resource to include start_date and end_date, and enforce logic ensuring only one academic year is Active at a time. The start_date and end_date must be valid before activation.

User Review Required
IMPORTANT

This change involves modifying the database schema. Since alembic is not configured, a manual migration script upgrade_academic_year.py will be created and executed to add start_date and end_date columns to the existing table without data loss.

Proposed Changes
Database Migration
[NEW] 
backend/upgrade_academic_year.py
Script to add start_date and end_date columns to academicyears (or appropriate table name) if they don't exist.
Backend Code
[MODIFY] 
backend/app/modules/academics/models.py
Add start_date (Date, nullable=True) and end_date (Date, nullable=True).
[MODIFY] 
backend/app/modules/academics/schemas.py
Add start_date and end_date to 
AcademicYearBase
, 
AcademicYearCreate
, AcademicYearUpdate, and 
AcademicYearResponse
.
[MODIFY] 
backend/app/modules/academics/router.py
Update 
create_academic_year
 to accept dates.
Update 
update_year_status
 or create a generic update endpoint:
Validate start_date and end_date are present and valid (start < end) before setting status to Active.
If status is being set to Active, check if any other year is Active. If so, reject or handle accordingly (User said "Only one academic year can be Active"). We will reject with 400.
Verification Plan
Automated Tests

Run upgrade_academic_year.py and check output.
Create a test script verify_academic_year.py to:
Create a Draft year with dates.
Try to Activate it (should succeed).
Create another Draft year.
Try to Activate the second one (should fail).
Archive the first one.
Activate the second one (should succeed).






Term Management Implementation Plan
Implement the relationship between 
AcademicYear
 and Term, including business logic for dates and status transitions.

Proposed Changes
Academics Module
[MODIFY] 
models.py
Add TermStatus enum (Draft, Active, Closed).
Add Term model with:
FK to 
AcademicYear
 (NOT NULL, ON DELETE RESTRICT).
name, status, start_date, end_date.
result_open_date, result_close_date.
sequence for sorting.
Add relationship between 
AcademicYear
 and Term.
[MODIFY] 
schemas.py
Add TermBase, TermCreate, TermUpdate, and TermResponse pydantic models.
[MODIFY] 
router.py
Implement POST /years/{year_id}/terms to create a term.
Implement GET /years/{year_id}/terms to list terms.
Implement PATCH /terms/{term_id} to update a term.
Implement validation logic:
Check dates within boundaries.
Prevent overlaps.
Ensure only one active term.
Validate result windows.





Term Management UI Implementation Plan
Implement the UI for managing academic terms within the academic years module.

Proposed Changes
Academics UI
[MODIFY] 
AdminAcademicYears.tsx
Add "Manage Term" button next to "New Academic Year".
Logic to open the modal for the activeYear when "Manage Term" is clicked.
[MODIFY] 
CreateAcademicYearModal.tsx
Add 
terms
 state to manage the list of terms.
Implement "Term Setup" section:
Header with "+ Add Term" button.
Repeatable term rows with fields for Name, Start Date, End Date.
Advanced collapsible section for Result Window dates.
Implementation of client-side validation for:
Start date < End date.
Term dates within Academic Year dates.
No overlapping terms.
Update 
handleSave
 to:
Validate terms.
Save terms sequentially after creating/updating the academic year.
Add status badges and activation logic for terms.
Verification Plan
Manual Verification
Open "New Academic Year" and add several terms.
Test validation:
Set a term date outside the year range.
Create overlapping terms.
Set result window outside term range.
Save as Draft and verify terms are persisted.
Try to activate a year and verify all terms must be valid.
Test "Set Active" for a term.





I have completed the Term Management UI. ***************************************************************************************************************

What's new:

Manage Term Button: You'll find a new button next to "New Academic Year" that opens the modal for the currently active year.
Enhanced Modal: The modal is now larger and includes a "Term Setup" section.
Dynamic Term Rows: You can add/remove terms. Each term has its own card with Name, Start Date, and End Date fields.
Advanced Settings: Each term row can be expanded to set "Result Window" dates (Open/Close).
Smart Validation: The UI checks in real-time if:
Term dates fall outside the academic year.
Terms overlap with each other.
End dates are before start dates.
Sequential Saving: When you click "Save", the system now carefully updates the Academic Year first and then creates/updates all term records sequentially.
Status Badges: You can see and manage statuses (Draft, Active, Closed) for each term.
Everything is connected to your backend and ready for testing!