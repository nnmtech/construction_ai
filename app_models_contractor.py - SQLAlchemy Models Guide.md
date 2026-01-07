# app/models/contractor.py - SQLAlchemy Models Guide

## Overview

The `app/models/contractor.py` file defines all SQLAlchemy ORM models for the Construction AI Landing Page application:

1. **Contractor** - Main contractor/company information
2. **ContactFormSubmission** - Contact form submissions
3. **ROICalculation** - ROI calculations and financial analysis
4. **DemoBooking** - Demo scheduling and booking information

---

## Database Schema Diagram

```
┌─────────────────────────────────────────┐
│         CONTRACTOR (Main Table)         │
├─────────────────────────────────────────┤
│ id (PK)                                 │
│ company_name                            │
│ contact_name                            │
│ email (UNIQUE)                          │
│ phone                                   │
│ company_size                            │
│ annual_revenue                          │
│ current_challenges                      │
│ estimated_annual_savings                │
│ roi_percentage                          │
│ demo_scheduled                          │
│ demo_date                               │
│ conversion_status                       │
│ created_at, updated_at                  │
└─────────────────────────────────────────┘
         ↑              ↑              ↑
         │              │              │
    (1:N)           (1:N)          (1:N)
         │              │              │
    ┌────┴───────┐  ┌───┴────────┐  ┌──┴──────────────┐
    │             │  │            │  │                 │
┌───┴──────────────────┐  ┌────────┴──────────┐  ┌────┴─────────────────┐
│ CONTACT_FORM_        │  │ ROI_CALCULATION   │  │ DEMO_BOOKING        │
│ SUBMISSION           │  │                   │  │                     │
├──────────────────────┤  ├───────────────────┤  ├─────────────────────┤
│ id (PK)              │  │ id (PK)           │  │ id (PK)             │
│ contractor_id (FK)   │  │ contractor_id(FK) │  │ contractor_id (FK)  │
│ company_name         │  │ avg_project_value │  │ demo_date           │
│ contact_name         │  │ avg_delay_%       │  │ attendee_name       │
│ email                │  │ projects_per_year │  │ attendee_email      │
│ phone                │  │ annual_delay_cost │  │ meeting_type        │
│ company_size         │  │ estimated_savings │  │ meeting_link        │
│ annual_revenue       │  │ roi_percentage    │  │ status              │
│ current_challenges   │  │ payback_months    │  │ demo_completed      │
│ status               │  │ created_at        │  │ follow_up_required  │
│ submission_date      │  │ updated_at        │  │ created_at          │
│ created_at           │  │                   │  │ updated_at          │
│ updated_at           │  │                   │  │                     │
└──────────────────────┘  └───────────────────┘  └─────────────────────┘
```

---

## Model 1: Contractor

### Purpose
Main table storing contractor/company information and engagement status.

### Table Name
`contractor`

### Columns

| Column | Type | Constraints | Purpose |
|--------|------|-----------|---------|
| `id` | Integer | PK, AUTO | Unique identifier |
| `company_name` | String(255) | NOT NULL, INDEX | Company name |
| `contact_name` | String(255) | NOT NULL | Primary contact person |
| `email` | String(255) | NOT NULL, UNIQUE, INDEX | Email (unique) |
| `phone` | String(20) | | Phone number |
| `company_size` | String(50) | INDEX | small, medium, large |
| `annual_revenue` | Float | | Annual revenue ($) |
| `current_challenges` | Text | | Business challenges |
| `estimated_annual_savings` | Float | | Estimated savings ($) |
| `roi_percentage` | Float | | ROI percentage |
| `demo_scheduled` | Boolean | DEFAULT=False, INDEX | Demo scheduled? |
| `demo_date` | DateTime | | Demo date/time |
| `demo_completed` | Boolean | DEFAULT=False | Demo completed? |
| `conversion_status` | String(50) | DEFAULT='lead', INDEX | lead, prospect, customer, lost |
| `welcome_email_sent` | Boolean | DEFAULT=False | Welcome email sent? |
| `roi_report_sent` | Boolean | DEFAULT=False | ROI report sent? |
| `last_email_sent_at` | DateTime | | Last email timestamp |
| `notes` | Text | | Internal notes |
| `created_at` | DateTime | NOT NULL, INDEX | Creation timestamp |
| `updated_at` | DateTime | NOT NULL | Update timestamp |

### Relationships

```python
# One-to-Many relationships
contact_submissions = relationship(
    "ContactFormSubmission",
    back_populates="contractor",
    cascade="all, delete-orphan"
)

roi_calculations = relationship(
    "ROICalculation",
    back_populates="contractor",
    cascade="all, delete-orphan"
)

demo_bookings = relationship(
    "DemoBooking",
    back_populates="contractor",
    cascade="all, delete-orphan"
)
```

### Indexes

- `idx_contractor_email` - Email (unique)
- `idx_contractor_company_name` - Company name
- `idx_contractor_company_size` - Company size
- `idx_contractor_created_at` - Creation date
- `idx_contractor_demo_scheduled` - Demo scheduled status
- `idx_contractor_conversion_status` - Conversion status

### Example Usage

```python
from app.database import SessionLocal
from app.models.contractor import Contractor

db = SessionLocal()

# Create contractor
contractor = Contractor(
    company_name="ABC Construction",
    contact_name="John Smith",
    email="john@abcconstruction.com",
    phone="404-555-0123",
    company_size="medium",
    annual_revenue=5000000,
    current_challenges="Schedule delays and subcontractor coordination"
)
db.add(contractor)
db.commit()

# Query contractors
contractors = db.query(Contractor).all()
contractor = db.query(Contractor).filter(
    Contractor.email == "john@abcconstruction.com"
).first()

# Update contractor
contractor.demo_scheduled = True
contractor.conversion_status = "prospect"
db.commit()

# Delete contractor
db.delete(contractor)
db.commit()
```

---

## Model 2: ContactFormSubmission

### Purpose
Tracks all contact form submissions with detailed information about inquiries.

### Table Name
`contact_form_submission`

### Columns

| Column | Type | Constraints | Purpose |
|--------|------|-----------|---------|
| `id` | Integer | PK, AUTO | Unique identifier |
| `contractor_id` | Integer | FK, NOT NULL, INDEX | Reference to Contractor |
| `company_name` | String(255) | NOT NULL | Company name from form |
| `contact_name` | String(255) | NOT NULL | Contact person from form |
| `email` | String(255) | NOT NULL, INDEX | Email from form |
| `phone` | String(20) | | Phone from form |
| `company_size` | String(50) | | Company size |
| `annual_revenue` | Float | | Annual revenue |
| `current_challenges` | Text | | Challenges described |
| `interested_features` | Text | | Interested features |
| `ip_address` | String(45) | | Submitter IP address |
| `user_agent` | String(500) | | Browser user agent |
| `referrer` | String(500) | | HTTP referrer |
| `status` | String(50) | DEFAULT='new', INDEX | new, contacted, qualified, disqualified |
| `notes` | Text | | Internal notes |
| `submission_date` | DateTime | NOT NULL, INDEX | Form submission time |
| `created_at` | DateTime | NOT NULL | Record creation time |
| `updated_at` | DateTime | NOT NULL | Record update time |

### Relationships

```python
contractor = relationship(
    "Contractor",
    back_populates="contact_submissions"
)
```

### Indexes

- `idx_contact_submission_contractor_id` - Contractor reference
- `idx_contact_submission_email` - Email
- `idx_contact_submission_submission_date` - Submission date
- `idx_contact_submission_status` - Status

### Example Usage

```python
from app.models.contractor import ContactFormSubmission

# Create submission
submission = ContactFormSubmission(
    contractor_id=1,
    company_name="ABC Construction",
    contact_name="John Smith",
    email="john@abcconstruction.com",
    phone="404-555-0123",
    company_size="medium",
    annual_revenue=5000000,
    current_challenges="Schedule delays and subcontractor coordination",
    status="new"
)
db.add(submission)
db.commit()

# Query submissions
submissions = db.query(ContactFormSubmission).filter(
    ContactFormSubmission.status == "new"
).all()

# Update submission status
submission.status = "contacted"
db.commit()
```

---

## Model 3: ROICalculation

### Purpose
Stores ROI calculations and financial analysis for contractors.

### Table Name
`roi_calculation`

### Columns

| Column | Type | Constraints | Purpose |
|--------|------|-----------|---------|
| `id` | Integer | PK, AUTO | Unique identifier |
| `contractor_id` | Integer | FK, NOT NULL, INDEX | Reference to Contractor |
| `avg_project_value` | Float | NOT NULL | Average project value ($) |
| `avg_delay_percentage` | Float | NOT NULL | Average delay (0-100%) |
| `num_projects_per_year` | Integer | NOT NULL | Projects per year |
| `avg_project_duration_days` | Integer | DEFAULT=180 | Project duration (days) |
| `cost_per_day_delay` | Float | NOT NULL | Cost per delay day ($) |
| `ai_solution_annual_cost` | Float | NOT NULL | AI solution cost ($) |
| `delay_reduction_percentage` | Float | NOT NULL | Delay reduction (0-1) |
| `days_delayed_per_project` | Float | | Calculated days delayed |
| `annual_delay_cost` | Float | | Calculated annual delay cost ($) |
| `estimated_savings_with_ai` | Float | | Estimated annual savings ($) |
| `payback_period_months` | Float | | Payback period (months) |
| `roi_percentage` | Float | | ROI percentage |
| `monthly_savings` | Float | | Monthly savings ($) |
| `break_even_months` | Float | | Break-even months |
| `three_year_savings` | Float | | 3-year savings ($) |
| `five_year_savings` | Float | | 5-year savings ($) |
| `notes` | Text | | Internal notes |
| `calculation_date` | DateTime | NOT NULL, INDEX | Calculation time |
| `created_at` | DateTime | NOT NULL | Record creation time |
| `updated_at` | DateTime | NOT NULL | Record update time |

### Relationships

```python
contractor = relationship(
    "Contractor",
    back_populates="roi_calculations"
)
```

### Indexes

- `idx_roi_calculation_contractor_id` - Contractor reference
- `idx_roi_calculation_calculation_date` - Calculation date

### Example Usage

```python
from app.models.contractor import ROICalculation

# Create ROI calculation
roi = ROICalculation(
    contractor_id=1,
    avg_project_value=500000,
    avg_delay_percentage=25,
    num_projects_per_year=12,
    cost_per_day_delay=45662,
    ai_solution_annual_cost=5000,
    delay_reduction_percentage=0.65,
    annual_delay_cost=24656880,
    estimated_savings_with_ai=16026972,
    payback_period_months=0.004,
    roi_percentage=320539
)
db.add(roi)
db.commit()

# Query ROI calculations
rois = db.query(ROICalculation).filter(
    ROICalculation.contractor_id == 1
).all()

# Get latest ROI for contractor
latest_roi = db.query(ROICalculation).filter(
    ROICalculation.contractor_id == 1
).order_by(ROICalculation.calculation_date.desc()).first()
```

---

## Model 4: DemoBooking

### Purpose
Stores information about scheduled demo sessions with contractors.

### Table Name
`demo_booking`

### Columns

| Column | Type | Constraints | Purpose |
|--------|------|-----------|---------|
| `id` | Integer | PK, AUTO | Unique identifier |
| `contractor_id` | Integer | FK, NOT NULL, INDEX | Reference to Contractor |
| `demo_date` | DateTime | NOT NULL, INDEX | Scheduled demo time |
| `demo_duration_minutes` | Integer | DEFAULT=30 | Demo duration (minutes) |
| `attendee_name` | String(255) | NOT NULL | Attendee name |
| `attendee_email` | String(255) | NOT NULL | Attendee email |
| `attendee_phone` | String(20) | | Attendee phone |
| `meeting_type` | String(50) | DEFAULT='zoom' | zoom, teams, phone, in_person |
| `meeting_link` | String(500) | | Meeting link/URL |
| `meeting_password` | String(50) | | Meeting password |
| `status` | String(50) | DEFAULT='scheduled', INDEX | scheduled, completed, cancelled, no_show, rescheduled |
| `cancellation_reason` | Text | | Cancellation reason |
| `demo_completed` | Boolean | DEFAULT=False | Demo completed? |
| `demo_feedback` | Text | | Demo feedback |
| `follow_up_required` | Boolean | DEFAULT=False | Follow-up needed? |
| `follow_up_date` | DateTime | | Follow-up date |
| `notes` | Text | | Internal notes |
| `created_at` | DateTime | NOT NULL, INDEX | Record creation time |
| `updated_at` | DateTime | NOT NULL | Record update time |

### Relationships

```python
contractor = relationship(
    "Contractor",
    back_populates="demo_bookings"
)
```

### Indexes

- `idx_demo_booking_contractor_id` - Contractor reference
- `idx_demo_booking_demo_date` - Demo date
- `idx_demo_booking_status` - Status

### Example Usage

```python
from app.models.contractor import DemoBooking
from datetime import datetime, timedelta

# Create demo booking
demo = DemoBooking(
    contractor_id=1,
    demo_date=datetime.now() + timedelta(days=3),
    demo_duration_minutes=30,
    attendee_name="John Smith",
    attendee_email="john@abcconstruction.com",
    attendee_phone="404-555-0123",
    meeting_type="zoom",
    meeting_link="https://zoom.us/j/123456789",
    status="scheduled"
)
db.add(demo)
db.commit()

# Query upcoming demos
upcoming_demos = db.query(DemoBooking).filter(
    DemoBooking.demo_date > datetime.now(),
    DemoBooking.status == "scheduled"
).all()

# Mark demo as completed
demo.status = "completed"
demo.demo_completed = True
demo.demo_feedback = "Very interested in the solution"
db.commit()
```

---

## Common Queries

### Get Contractor with All Related Data

```python
from sqlalchemy.orm import joinedload

contractor = db.query(Contractor).options(
    joinedload(Contractor.contact_submissions),
    joinedload(Contractor.roi_calculations),
    joinedload(Contractor.demo_bookings)
).filter(Contractor.id == 1).first()
```

### Get Contractors by Conversion Status

```python
prospects = db.query(Contractor).filter(
    Contractor.conversion_status == "prospect"
).all()

customers = db.query(Contractor).filter(
    Contractor.conversion_status == "customer"
).all()
```

### Get Contractors with Scheduled Demos

```python
demo_scheduled = db.query(Contractor).filter(
    Contractor.demo_scheduled == True
).all()
```

### Get Recent Contact Submissions

```python
from datetime import datetime, timedelta

recent = db.query(ContactFormSubmission).filter(
    ContactFormSubmission.submission_date >= datetime.now() - timedelta(days=7)
).order_by(ContactFormSubmission.submission_date.desc()).all()
```

### Get High-Value Opportunities

```python
high_value = db.query(Contractor).filter(
    Contractor.estimated_annual_savings > 1000000
).order_by(Contractor.estimated_annual_savings.desc()).all()
```

### Get Upcoming Demos

```python
from datetime import datetime

upcoming = db.query(DemoBooking).filter(
    DemoBooking.demo_date > datetime.now(),
    DemoBooking.status == "scheduled"
).order_by(DemoBooking.demo_date).all()
```

---

## Model Methods

### Contractor.to_dict()

```python
contractor = db.query(Contractor).first()
data = contractor.to_dict()
# Returns dictionary with all contractor data
```

### ContactFormSubmission.to_dict()

```python
submission = db.query(ContactFormSubmission).first()
data = submission.to_dict()
# Returns dictionary with all submission data
```

### ROICalculation.to_dict()

```python
roi = db.query(ROICalculation).first()
data = roi.to_dict()
# Returns dictionary with all ROI data
```

### DemoBooking.to_dict()

```python
demo = db.query(DemoBooking).first()
data = demo.to_dict()
# Returns dictionary with all booking data
```

---

## Cascade Behavior

All relationships use `cascade="all, delete-orphan"`:

- When a **Contractor** is deleted, all related **ContactFormSubmission**, **ROICalculation**, and **DemoBooking** records are automatically deleted
- This ensures referential integrity and prevents orphaned records

---

## Indexes Summary

| Table | Index | Columns | Purpose |
|-------|-------|---------|---------|
| contractor | idx_contractor_email | email | Unique lookup |
| contractor | idx_contractor_company_name | company_name | Search by company |
| contractor | idx_contractor_company_size | company_size | Filter by size |
| contractor | idx_contractor_created_at | created_at | Sort by date |
| contractor | idx_contractor_demo_scheduled | demo_scheduled | Find demos |
| contractor | idx_contractor_conversion_status | conversion_status | Filter by status |
| contact_form_submission | idx_contact_submission_contractor_id | contractor_id | Join queries |
| contact_form_submission | idx_contact_submission_email | email | Email lookup |
| contact_form_submission | idx_contact_submission_submission_date | submission_date | Sort by date |
| contact_form_submission | idx_contact_submission_status | status | Filter by status |
| roi_calculation | idx_roi_calculation_contractor_id | contractor_id | Join queries |
| roi_calculation | idx_roi_calculation_calculation_date | calculation_date | Sort by date |
| demo_booking | idx_demo_booking_contractor_id | contractor_id | Join queries |
| demo_booking | idx_demo_booking_demo_date | demo_date | Find upcoming |
| demo_booking | idx_demo_booking_status | status | Filter by status |

---

## File Placement

```
app/
├── __init__.py
├── models/
│   ├── __init__.py
│   └── contractor.py          # ← This file
├── schemas/
├── routes/
├── database.py
├── main.py
└── ...
```

---

## Summary

The models provide:

✅ **Four comprehensive tables** - Contractor, ContactFormSubmission, ROICalculation, DemoBooking
✅ **Proper relationships** - One-to-Many with cascade delete
✅ **Optimized indexes** - For common queries
✅ **Timestamps** - created_at and updated_at on all tables
✅ **Helper methods** - to_dict() and __repr__() on all models
✅ **Comprehensive documentation** - Docstrings on all columns
✅ **Data validation** - Constraints and types
✅ **Production-ready** - Scalable and maintainable

This provides a complete, production-ready database layer for the FastAPI application!
