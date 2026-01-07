# app/models/contractor.py - Complete Contractor Models Guide

## Overview

The `contractor.py` module contains three core SQLAlchemy ORM models for the Construction AI Landing Page application.

**Purpose:**
- Store contractor/company information
- Track contact form submissions
- Store ROI calculation results
- Manage relationships between models

---

## Models

### 1. Contractor Model

**Table Name:** `contractors`

**Purpose:** Store construction contractor/company information

#### Columns

**Primary Key:**
- `id` (Integer): Unique contractor identifier

**Company Information:**
- `company_name` (String 255): Name of construction company (indexed)
- `contact_name` (String 255): Name of primary contact
- `email` (String 255): Contact email (unique, indexed)
- `phone` (String 20): Contact phone number
- `company_size` (String 50): Company size - small/medium/large (indexed)
- `annual_revenue` (Float): Company's annual revenue

**Engagement:**
- `current_challenges` (Text): Description of current challenges
- `notes` (Text): Additional notes

**ROI Information:**
- `estimated_annual_savings` (Float): Estimated annual savings
- `roi_percentage` (Float): Return on investment percentage
- `payback_period_months` (Float): Payback period in months

**Demo Booking:**
- `demo_scheduled` (Boolean): Whether demo is scheduled (indexed)
- `demo_date` (DateTime): Date/time of scheduled demo
- `demo_completed` (Boolean): Whether demo was completed

**Engagement Status:**
- `conversion_status` (String 50): lead/prospect/customer/lost (indexed)

**Email Tracking:**
- `welcome_email_sent` (Boolean): Welcome email sent status
- `roi_report_sent` (Boolean): ROI report sent status
- `last_email_sent_at` (DateTime): Last email timestamp

**Timestamps:**
- `created_at` (DateTime): Record creation timestamp (indexed)
- `updated_at` (DateTime): Last update timestamp

#### Relationships

**One-to-Many: Contractor → ContactFormSubmission**
- Contractor can have multiple submissions
- Cascade delete enabled

**One-to-Many: Contractor → ROICalculation**
- Contractor can have multiple ROI calculations
- Cascade delete enabled

**One-to-Many: Contractor → DemoBooking**
- Contractor can have multiple demo bookings
- Cascade delete enabled

#### Indexes (6 total)

| Index | Columns | Type | Purpose |
|-------|---------|------|---------|
| ix_contractor_email | email | UNIQUE | Fast lookup by email |
| ix_contractor_company_name | company_name | NORMAL | Filter by company |
| ix_contractor_company_size | company_size | NORMAL | Filter by size |
| ix_contractor_created_at | created_at | NORMAL | Sort by date |
| ix_contractor_demo_scheduled | demo_scheduled | NORMAL | Filter scheduled |
| ix_contractor_conversion_status | conversion_status | NORMAL | Filter by status |

#### Methods

**`__repr__()`**
```python
contractor = Contractor(email="john@abc.com", company_name="ABC")
print(contractor)
# Output: <Contractor(id=1, email=john@abc.com, company=ABC)>
```

**`to_dict()`**
```python
contractor_dict = contractor.to_dict()
# Returns all contractor fields as dictionary
```

**`schedule_demo(demo_date)`**
```python
from datetime import datetime, timezone
demo_date = datetime(2026, 1, 15, 10, 0, 0, tzinfo=timezone.utc)
contractor.schedule_demo(demo_date)
db.commit()
```

**`complete_demo()`**
```python
contractor.complete_demo()
db.commit()
```

**`update_conversion_status(status)`**
```python
contractor.update_conversion_status("prospect")
db.commit()
```

**`set_roi_data(savings, roi_pct, payback_months)`**
```python
contractor.set_roi_data(
    savings=885441,
    roi_pct=17609,
    payback_months=0.07
)
db.commit()
```

**`mark_welcome_email_sent()`**
```python
contractor.mark_welcome_email_sent()
db.commit()
```

**`mark_roi_report_sent()`**
```python
contractor.mark_roi_report_sent()
db.commit()
```

**`get_submission_count()`**
```python
count = contractor.get_submission_count()
```

**`get_roi_calculation_count()`**
```python
count = contractor.get_roi_calculation_count()
```

**`get_demo_booking_count()`**
```python
count = contractor.get_demo_booking_count()
```

---

### 2. ContactFormSubmission Model

**Table Name:** `contact_form_submissions`

**Purpose:** Track all contact form submissions

#### Columns

**Primary Key:**
- `id` (Integer): Unique submission identifier

**Foreign Key:**
- `contractor_id` (Integer): Foreign key to Contractor (indexed)

**Submission Data:**
- `company_name` (String 255): Company name from form
- `contact_name` (String 255): Contact name from form
- `email` (String 255): Email from form (indexed)
- `phone` (String 20): Phone from form
- `company_size` (String 50): Company size from form
- `annual_revenue` (Float): Revenue from form
- `current_challenges` (Text): Challenges from form
- `interested_features` (Text): Features interested in

**Tracking Data:**
- `ip_address` (String 45): Submitter's IP address
- `user_agent` (String 500): Submitter's user agent
- `referrer` (String 500): HTTP referrer

**Status:**
- `status` (String 50): new/contacted/qualified/disqualified (indexed)
- `submission_date` (DateTime): Date of submission (indexed)

**Timestamps:**
- `created_at` (DateTime): Record creation timestamp
- `updated_at` (DateTime): Last update timestamp

#### Relationships

**Many-to-One: ContactFormSubmission → Contractor**
- Multiple submissions belong to one contractor
- Cascade delete enabled

#### Indexes (4 total)

| Index | Columns | Type | Purpose |
|-------|---------|------|---------|
| ix_submission_contractor_id | contractor_id | NORMAL | Link to contractor |
| ix_submission_email | email | NORMAL | Filter by email |
| ix_submission_submission_date | submission_date | NORMAL | Sort by date |
| ix_submission_status | status | NORMAL | Filter by status |

#### Methods

**`__repr__()`**
```python
submission = ContactFormSubmission(email="john@abc.com")
print(submission)
# Output: <ContactFormSubmission(id=1, email=john@abc.com)>
```

**`to_dict()`**
```python
submission_dict = submission.to_dict()
# Returns all submission fields as dictionary
```

---

### 3. ROICalculation Model

**Table Name:** `roi_calculations`

**Purpose:** Store ROI calculation results

#### Columns

**Primary Key:**
- `id` (Integer): Unique calculation identifier

**Foreign Key:**
- `contractor_id` (Integer): Foreign key to Contractor (indexed)

**Input Data:**
- `email` (String 255): Contractor's email
- `project_value` (Float): Average project value
- `delay_percentage` (Float): Percentage of projects delayed
- `projects_per_year` (Integer): Number of projects per year
- `avg_delay_days` (Float): Average delay in days

**Calculated Data:**
- `annual_delay_cost` (Float): Annual cost of delays
- `estimated_annual_savings` (Float): Estimated savings with AI
- `monthly_savings` (Float): Monthly savings
- `ai_solution_annual_cost` (Float): Annual cost of AI solution
- `net_annual_benefit` (Float): Net annual benefit
- `payback_period_months` (Float): Payback period
- `roi_percentage` (Float): ROI percentage
- `break_even_months` (Float): Break-even period

**Timestamps:**
- `calculation_date` (DateTime): Date of calculation (indexed)
- `created_at` (DateTime): Record creation timestamp

#### Relationships

**Many-to-One: ROICalculation → Contractor**
- Multiple calculations belong to one contractor
- Cascade delete enabled

#### Indexes (2 total)

| Index | Columns | Type | Purpose |
|-------|---------|------|---------|
| ix_roi_contractor_id | contractor_id | NORMAL | Link to contractor |
| ix_roi_calculation_date | calculation_date | NORMAL | Sort by date |

#### Methods

**`__repr__()`**
```python
roi = ROICalculation(contractor_id=1)
print(roi)
# Output: <ROICalculation(id=1, contractor_id=1)>
```

**`to_dict()`**
```python
roi_dict = roi.to_dict()
# Returns all ROI fields as dictionary
```

---

## Enumerations

### CompanySizeEnum
```python
class CompanySizeEnum(str, enum.Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
```

### ConversionStatusEnum
```python
class ConversionStatusEnum(str, enum.Enum):
    LEAD = "lead"
    PROSPECT = "prospect"
    CUSTOMER = "customer"
    LOST = "lost"
```

### SubmissionStatusEnum
```python
class SubmissionStatusEnum(str, enum.Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    DISQUALIFIED = "disqualified"
```

---

## Common Queries

### Find Contractor by Email
```python
contractor = db.query(Contractor).filter_by(email="john@abc.com").first()
```

### Find All Contractors by Company Size
```python
medium_contractors = db.query(Contractor).filter_by(company_size="medium").all()
```

### Find Contractors with Scheduled Demos
```python
demo_contractors = db.query(Contractor).filter_by(demo_scheduled=True).all()
```

### Find Contractors by Conversion Status
```python
prospects = db.query(Contractor).filter_by(conversion_status="prospect").all()
```

### Get Contractor with All Submissions
```python
contractor = db.query(Contractor).filter_by(email="john@abc.com").first()
submissions = contractor.contact_form_submissions
```

### Get Contractor with All ROI Calculations
```python
contractor = db.query(Contractor).filter_by(email="john@abc.com").first()
roi_calcs = contractor.roi_calculations
```

### Get Contractor with All Demo Bookings
```python
contractor = db.query(Contractor).filter_by(email="john@abc.com").first()
bookings = contractor.demo_bookings
```

### Count Contractors by Status
```python
leads = db.query(Contractor).filter_by(conversion_status="lead").count()
prospects = db.query(Contractor).filter_by(conversion_status="prospect").count()
customers = db.query(Contractor).filter_by(conversion_status="customer").count()
```

### Find Recently Created Contractors
```python
from datetime import datetime, timedelta, timezone

seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
new_contractors = db.query(Contractor).filter(
    Contractor.created_at >= seven_days_ago
).all()
```

### Get Contractor Statistics
```python
total = db.query(Contractor).count()
with_demos = db.query(Contractor).filter_by(demo_scheduled=True).count()
completed_demos = db.query(Contractor).filter_by(demo_completed=True).count()
customers = db.query(Contractor).filter_by(conversion_status="customer").count()

stats = {
    "total_contractors": total,
    "with_scheduled_demos": with_demos,
    "completed_demos": completed_demos,
    "customers": customers
}
```

### Get Submissions by Contractor
```python
contractor = db.query(Contractor).filter_by(email="john@abc.com").first()
submissions = db.query(ContactFormSubmission).filter_by(
    contractor_id=contractor.id
).all()
```

### Get ROI Calculations by Contractor
```python
contractor = db.query(Contractor).filter_by(email="john@abc.com").first()
roi_calcs = db.query(ROICalculation).filter_by(
    contractor_id=contractor.id
).all()
```

---

## Usage Examples

### Create Contractor
```python
contractor = Contractor(
    company_name="ABC Construction",
    contact_name="John Smith",
    email="john@abcconstruction.com",
    phone="404-555-0123",
    company_size="medium",
    annual_revenue=5000000,
    current_challenges="Schedule delays and coordination"
)
db.add(contractor)
db.commit()
db.refresh(contractor)
print(f"Contractor created: {contractor.id}")
```

### Create Contact Form Submission
```python
submission = ContactFormSubmission(
    contractor_id=contractor.id,
    company_name="ABC Construction",
    contact_name="John Smith",
    email="john@abcconstruction.com",
    phone="404-555-0123",
    company_size="medium",
    current_challenges="Schedule delays",
    ip_address="192.168.1.1",
    user_agent="Mozilla/5.0..."
)
db.add(submission)
db.commit()
```

### Create ROI Calculation
```python
roi = ROICalculation(
    contractor_id=contractor.id,
    email="john@abcconstruction.com",
    project_value=500000,
    delay_percentage=75,
    projects_per_year=4,
    avg_delay_days=37,
    annual_delay_cost=1369860,
    estimated_annual_savings=885441,
    monthly_savings=73787,
    ai_solution_annual_cost=5000,
    net_annual_benefit=880441,
    payback_period_months=0.07,
    roi_percentage=17609,
    break_even_months=0.07
)
db.add(roi)
db.commit()
```

### Update Contractor Status
```python
contractor = db.query(Contractor).filter_by(email="john@abc.com").first()

if contractor:
    # Update conversion status
    contractor.update_conversion_status("prospect")
    
    # Set ROI data
    contractor.set_roi_data(
        savings=885441,
        roi_pct=17609,
        payback_months=0.07
    )
    
    # Schedule demo
    from datetime import datetime, timezone
    demo_date = datetime(2026, 1, 15, 10, 0, 0, tzinfo=timezone.utc)
    contractor.schedule_demo(demo_date)
    
    # Mark emails as sent
    contractor.mark_welcome_email_sent()
    contractor.mark_roi_report_sent()
    
    # Commit changes
    db.commit()
```

### Get Contractor with All Data
```python
contractor = db.query(Contractor).filter_by(email="john@abc.com").first()

if contractor:
    print(f"Company: {contractor.company_name}")
    print(f"Contact: {contractor.contact_name}")
    print(f"Status: {contractor.conversion_status}")
    print(f"ROI: {contractor.roi_percentage}%")
    print(f"Submissions: {contractor.get_submission_count()}")
    print(f"ROI Calcs: {contractor.get_roi_calculation_count()}")
    print(f"Demo Bookings: {contractor.get_demo_booking_count()}")
    
    # Get related data
    for submission in contractor.contact_form_submissions:
        print(f"  Submission: {submission.submission_date}")
    
    for roi in contractor.roi_calculations:
        print(f"  ROI: {roi.roi_percentage}%")
    
    for booking in contractor.demo_bookings:
        print(f"  Demo: {booking.demo_date}")
```

---

## Relationships Diagram

```
User
  ├── ContactFormSubmission (1:N)
  ├── ROICalculation (1:N)
  └── DemoBooking (1:N)

Contractor
  ├── ContactFormSubmission (1:N)
  ├── ROICalculation (1:N)
  └── DemoBooking (1:N)

ContactFormSubmission
  └── Contractor (N:1)

ROICalculation
  └── Contractor (N:1)

DemoBooking
  ├── Contractor (N:1)
  └── User (N:1)
```

---

## Data Integrity

### Cascade Delete
- Deleting a Contractor automatically deletes all related:
  - ContactFormSubmissions
  - ROICalculations
  - DemoBookings

### Unique Constraints
- Email is unique per Contractor
- Prevents duplicate contractors

### Foreign Key Constraints
- All foreign keys enforced
- Referential integrity maintained

---

## File Placement

```
app/
├── models/
│   ├── __init__.py
│   ├── contractor.py            # ← This file
│   ├── booking.py
│   └── user.py
├── routes/
├── schemas/
├── database.py
└── main.py
```

---

## Integration

### Update models/__init__.py
```python
from app.models.contractor import (
    Contractor,
    ContactFormSubmission,
    ROICalculation,
    CompanySizeEnum,
    ConversionStatusEnum,
    SubmissionStatusEnum
)

__all__ = [
    "Contractor",
    "ContactFormSubmission",
    "ROICalculation",
    "CompanySizeEnum",
    "ConversionStatusEnum",
    "SubmissionStatusEnum"
]
```

---

## Summary

The contractor models provide:

✅ **Contractor Management** - Store company information
✅ **Contact Form Tracking** - Track all submissions
✅ **ROI Calculation Storage** - Store calculation results
✅ **Relationships** - Links between models
✅ **Cascade Delete** - Data integrity
✅ **Indexes** - Performance optimization (12 total)
✅ **Utility Methods** - Common operations
✅ **Enumerations** - Type-safe enums
✅ **Audit Trail** - Timestamps for all records
✅ **Email Tracking** - Track email sends
✅ **Demo Management** - Schedule and track demos
✅ **Status Tracking** - Conversion status
✅ **Production-ready** - Fully tested and documented

Everything is production-ready and fully documented!
