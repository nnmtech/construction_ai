# app/models/user.py - User Model Guide

## Overview

The `User` model is the core SQLAlchemy ORM model for user authentication and account management.

**Purpose:**
- Store user account information
- Manage authentication credentials
- Track email verification status
- Maintain audit trail with timestamps
- Establish relationships with other models

---

## Table Structure

**Table Name:** `users`

---

## Columns

### Primary Key

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PRIMARY KEY, INDEX | Unique user identifier |

---

### Account Information

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| company_name | String(255) | NOT NULL, INDEX | User's company name |
| contact_name | String(255) | NOT NULL | User's full name |
| email | String(255) | NOT NULL, UNIQUE, INDEX | User's email address |
| phone | String(20) | NULLABLE | User's phone number |
| company_size | String(50) | NULLABLE | Company size (small/medium/large) |

---

### Authentication

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| password_hash | String(255) | NOT NULL | Hashed password (bcrypt) |

---

### Verification & Status

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| email_verified | Boolean | NOT NULL, DEFAULT False, INDEX | Email verification status |
| email_verified_at | DateTime | NULLABLE | Email verification timestamp |
| is_active | Boolean | NOT NULL, DEFAULT True, INDEX | Account active status |

---

### Timestamps

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| created_at | DateTime | NOT NULL, DEFAULT NOW, INDEX | Account creation timestamp |
| updated_at | DateTime | NOT NULL, DEFAULT NOW, ONUPDATE NOW | Last update timestamp |
| last_login_at | DateTime | NULLABLE | Last login timestamp |

---

## Relationships

### One-to-Many: User → ContactFormSubmission

```python
contact_form_submissions = relationship(
    "ContactFormSubmission",
    back_populates="user",
    cascade="all, delete-orphan",
    lazy="select"
)
```

**Features:**
- User can have multiple contact form submissions
- Cascade delete: Deleting user deletes all submissions
- Lazy loading: Load on access

**Usage:**
```python
user = db.query(User).first()
for submission in user.contact_form_submissions:
    print(submission.company_name)
```

---

### One-to-Many: User → ROICalculation

```python
roi_calculations = relationship(
    "ROICalculation",
    back_populates="user",
    cascade="all, delete-orphan",
    lazy="select"
)
```

**Features:**
- User can have multiple ROI calculations
- Cascade delete: Deleting user deletes all calculations
- Lazy loading: Load on access

**Usage:**
```python
user = db.query(User).first()
for roi in user.roi_calculations:
    print(roi.roi_percentage)
```

---

### One-to-Many: User → DemoBooking

```python
demo_bookings = relationship(
    "DemoBooking",
    back_populates="user",
    cascade="all, delete-orphan",
    lazy="select"
)
```

**Features:**
- User can have multiple demo bookings
- Cascade delete: Deleting user deletes all bookings
- Lazy loading: Load on access

**Usage:**
```python
user = db.query(User).first()
for booking in user.demo_bookings:
    print(booking.demo_date)
```

---

## Indexes

| Index Name | Columns | Type | Purpose |
|------------|---------|------|---------|
| ix_user_email | email | UNIQUE | Fast lookup by email |
| ix_user_email_verified | email_verified | NORMAL | Filter verified users |
| ix_user_is_active | is_active | NORMAL | Filter active users |
| ix_user_created_at | created_at | NORMAL | Sort by creation date |
| ix_user_company_name | company_name | NORMAL | Filter by company |

---

## Methods

### String Representation

**`__repr__()`**
```python
user = User(email="john@example.com", company_name="ABC")
print(user)
# Output: <User(id=1, email=john@example.com, company=ABC)>
```

---

### Conversion

**`to_dict(include_password=False)`**

Converts User object to dictionary.

**Parameters:**
- `include_password` (bool): Include password hash (default: False)

**Returns:**
- Dictionary with all user fields

**Example:**
```python
user = db.query(User).first()
user_dict = user.to_dict()
# Returns: {
#     "id": 1,
#     "company_name": "ABC Construction",
#     "contact_name": "John Smith",
#     "email": "john@example.com",
#     "phone": "404-555-0123",
#     "company_size": "medium",
#     "email_verified": True,
#     "email_verified_at": "2026-01-05T10:30:00+00:00",
#     "is_active": True,
#     "created_at": "2026-01-05T10:30:00+00:00",
#     "updated_at": "2026-01-05T10:30:00+00:00",
#     "last_login_at": "2026-01-06T14:22:00+00:00"
# }
```

---

### Email Verification

**`mark_email_verified()`**

Mark user's email as verified.

**Example:**
```python
user = db.query(User).filter_by(email="john@example.com").first()
user.mark_email_verified()
db.commit()
```

**`is_email_verified()`**

Check if user's email is verified.

**Example:**
```python
if user.is_email_verified():
    print("Email is verified")
```

---

### Account Status

**`deactivate()`**

Deactivate user account.

**Example:**
```python
user.deactivate()
db.commit()
```

**`activate()`**

Activate user account.

**Example:**
```python
user.activate()
db.commit()
```

**`is_account_active()`**

Check if user's account is active.

**Example:**
```python
if user.is_account_active():
    print("Account is active")
```

---

### Login Tracking

**`update_last_login()`**

Update last login timestamp.

**Example:**
```python
user.update_last_login()
db.commit()
```

**`get_days_since_last_login()`**

Get days since last login.

**Returns:**
- Integer (days) or None if never logged in

**Example:**
```python
days = user.get_days_since_last_login()
if days and days > 30:
    print("User hasn't logged in for 30+ days")
```

---

### Account Age

**`get_account_age_days()`**

Get account age in days.

**Returns:**
- Integer (days)

**Example:**
```python
age = user.get_account_age_days()
print(f"Account is {age} days old")
```

---

### Interaction Counts

**`get_submission_count()`**

Get number of contact form submissions.

**Returns:**
- Integer (count)

**Example:**
```python
count = user.get_submission_count()
print(f"User has {count} submissions")
```

**`get_roi_calculation_count()`**

Get number of ROI calculations.

**Returns:**
- Integer (count)

**Example:**
```python
count = user.get_roi_calculation_count()
print(f"User has {count} ROI calculations")
```

**`get_demo_booking_count()`**

Get number of demo bookings.

**Returns:**
- Integer (count)

**Example:**
```python
count = user.get_demo_booking_count()
print(f"User has {count} demo bookings")
```

**`get_total_interactions()`**

Get total number of interactions.

**Returns:**
- Integer (submissions + ROI + bookings)

**Example:**
```python
total = user.get_total_interactions()
print(f"User has {total} total interactions")
```

---

## Hybrid Properties

### `account_age_days`

Account age in days (usable in queries).

**Example:**
```python
# Get users with accounts older than 30 days
old_users = db.query(User).filter(User.account_age_days > 30).all()
```

---

### `days_since_last_login`

Days since last login (usable in queries).

**Example:**
```python
# Get users who haven't logged in for 7+ days
inactive_users = db.query(User).filter(User.days_since_last_login > 7).all()
```

---

## Common Queries

### Find User by Email
```python
user = db.query(User).filter_by(email="john@example.com").first()
```

### Find Active Users
```python
active_users = db.query(User).filter_by(is_active=True).all()
```

### Find Verified Users
```python
verified_users = db.query(User).filter_by(email_verified=True).all()
```

### Find Users by Company
```python
company_users = db.query(User).filter_by(company_name="ABC Construction").all()
```

### Find Users by Company Size
```python
medium_companies = db.query(User).filter_by(company_size="medium").all()
```

### Find Recently Created Users
```python
from datetime import datetime, timedelta, timezone

seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
new_users = db.query(User).filter(User.created_at >= seven_days_ago).all()
```

### Find Users Who Haven't Logged In
```python
no_login = db.query(User).filter(User.last_login_at == None).all()
```

### Count Active Users
```python
active_count = db.query(User).filter_by(is_active=True).count()
```

### Get User Statistics
```python
total_users = db.query(User).count()
verified_users = db.query(User).filter_by(email_verified=True).count()
active_users = db.query(User).filter_by(is_active=True).count()
inactive_users = db.query(User).filter_by(is_active=False).count()

stats = {
    "total": total_users,
    "verified": verified_users,
    "active": active_users,
    "inactive": inactive_users
}
```

---

## Usage Examples

### Create User
```python
from app.security import hash_password

user = User(
    company_name="ABC Construction",
    contact_name="John Smith",
    email="john@abcconstruction.com",
    password_hash=hash_password("SecurePass123!"),
    phone="404-555-0123",
    company_size="medium"
)
db.add(user)
db.commit()
db.refresh(user)
print(f"User created: {user.id}")
```

### Find and Update User
```python
user = db.query(User).filter_by(email="john@example.com").first()

if user:
    # Mark email as verified
    user.mark_email_verified()
    
    # Update last login
    user.update_last_login()
    
    # Commit changes
    db.commit()
    print("User updated")
```

### Check User Status
```python
user = db.query(User).filter_by(email="john@example.com").first()

if user:
    print(f"Active: {user.is_account_active()}")
    print(f"Email Verified: {user.is_email_verified()}")
    print(f"Account Age: {user.get_account_age_days()} days")
    print(f"Last Login: {user.get_days_since_last_login()} days ago")
    print(f"Total Interactions: {user.get_total_interactions()}")
```

### Deactivate User
```python
user = db.query(User).filter_by(email="john@example.com").first()

if user:
    user.deactivate()
    db.commit()
    print("User deactivated")
```

### Get User with Relationships
```python
user = db.query(User).filter_by(email="john@example.com").first()

if user:
    # Get all submissions
    submissions = user.contact_form_submissions
    print(f"Submissions: {len(submissions)}")
    
    # Get all ROI calculations
    roi_calcs = user.roi_calculations
    print(f"ROI Calculations: {len(roi_calcs)}")
    
    # Get all demo bookings
    bookings = user.demo_bookings
    print(f"Demo Bookings: {len(bookings)}")
```

### Convert to Dictionary
```python
user = db.query(User).filter_by(email="john@example.com").first()

if user:
    user_dict = user.to_dict()
    print(user_dict)
    # Returns all user fields as dictionary
```

---

## Data Types

| Field | Type | Example |
|-------|------|---------|
| id | int | 1 |
| company_name | str | "ABC Construction" |
| contact_name | str | "John Smith" |
| email | str | "john@example.com" |
| phone | str | "404-555-0123" |
| company_size | str | "medium" |
| password_hash | str | "$2b$12$..." |
| email_verified | bool | True |
| email_verified_at | datetime | 2026-01-05T10:30:00+00:00 |
| is_active | bool | True |
| created_at | datetime | 2026-01-05T10:30:00+00:00 |
| updated_at | datetime | 2026-01-06T14:22:00+00:00 |
| last_login_at | datetime | 2026-01-06T14:22:00+00:00 |

---

## Constraints

| Constraint | Description |
|-----------|-------------|
| PRIMARY KEY (id) | Unique identifier |
| UNIQUE (email) | Email must be unique |
| NOT NULL | Required fields |
| DEFAULT False | email_verified defaults to False |
| DEFAULT True | is_active defaults to True |
| CASCADE DELETE | Delete user deletes all related records |

---

## File Placement

```
app/
├── models/
│   ├── __init__.py
│   ├── contractor.py
│   ├── booking.py
│   └── user.py                  # ← This file
├── routes/
├── schemas/
├── database.py
└── main.py
```

---

## Integration with Database

### Update database.py

Add User model import to `app/database.py`:

```python
from app.models.user import User
```

### Update models/__init__.py

Add User to `app/models/__init__.py`:

```python
from app.models.contractor import Contractor, ContactFormSubmission, ROICalculation
from app.models.booking import DemoBooking
from app.models.user import User

__all__ = [
    "Contractor",
    "ContactFormSubmission",
    "ROICalculation",
    "DemoBooking",
    "User"
]
```

---

## Summary

The User model provides:

✅ **User Account Management** - Store user information
✅ **Authentication** - Password hashing and verification
✅ **Email Verification** - Track email verification status
✅ **Account Status** - Active/inactive status
✅ **Login Tracking** - Last login timestamp
✅ **Audit Trail** - Creation and update timestamps
✅ **Relationships** - Links to submissions, ROI, bookings
✅ **Utility Methods** - Common operations
✅ **Hybrid Properties** - Queryable properties
✅ **Indexes** - Performance optimization
✅ **Cascade Delete** - Data integrity
✅ **Production-ready** - Fully tested and documented

Everything is production-ready and fully documented!
