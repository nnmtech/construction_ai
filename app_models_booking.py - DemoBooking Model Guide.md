# app/models/booking.py - DemoBooking Model Guide

## Overview

The `app/models/booking.py` module defines the SQLAlchemy ORM model for demo bookings.

**Purpose:**
- Store demo appointment information
- Track booking status and lifecycle
- Manage contractor relationships
- Provide query methods for common operations

---

## DemoBooking Model

### Table Name
`demo_bookings`

### Columns

#### Primary Key
- **id** (Integer): Unique booking identifier

#### Foreign Keys
- **contractor_id** (Integer): Foreign key to Contractor table
  - Cascade delete enabled
  - Indexed for performance

#### Booking Information
- **demo_date** (DateTime): Date and time of demo appointment (UTC)
  - Indexed for sorting and filtering
  - Stores complete datetime with timezone

- **status** (String): Booking status
  - Values: scheduled, confirmed, completed, cancelled, rescheduled
  - Default: scheduled
  - Indexed for filtering

- **preferred_contact_method** (String): Preferred contact method
  - Values: phone, email, video
  - Default: video
  - Stores contractor preference

- **notes** (Text): Additional notes or questions
  - Optional field
  - Stores contractor questions and preferences

- **zoom_link** (String): Zoom meeting link
  - Optional field
  - Stores video conference URL
  - Max 500 characters

- **confirmation_sent** (Boolean): Whether confirmation email was sent
  - Default: False
  - Tracks email delivery

#### Timestamps
- **created_at** (DateTime): Record creation timestamp (UTC)
  - Indexed for sorting
  - Auto-set on creation

- **updated_at** (DateTime): Record update timestamp (UTC)
  - Auto-updated on changes
  - Tracks last modification

---

## Relationships

### Contractor (Many-to-One)
```python
contractor = relationship(
    "Contractor",
    back_populates="demo_bookings",
    lazy="joined"
)
```

**Features:**
- ✅ Lazy loading set to "joined" for performance
- ✅ Back-populates for bidirectional access
- ✅ Cascade delete when contractor is deleted

**Usage:**
```python
booking = db.query(DemoBooking).first()
print(booking.contractor.company_name)
```

---

## Indexes

### Single Column Indexes
- `contractor_id` - For filtering by contractor
- `demo_date` - For sorting by date
- `status` - For filtering by status
- `created_at` - For sorting by creation date

### Composite Indexes
- `(contractor_id, demo_date)` - For contractor-specific date queries
- `(status, demo_date)` - For status-specific date queries

**Benefits:**
- ✅ Fast filtering by contractor
- ✅ Efficient date range queries
- ✅ Quick status lookups
- ✅ Optimized composite queries

---

## Status Enum

### Valid Statuses
```python
SCHEDULED = "scheduled"      # Initial booking
CONFIRMED = "confirmed"      # Contractor confirmed
COMPLETED = "completed"      # Demo completed
CANCELLED = "cancelled"      # Booking cancelled
RESCHEDULED = "rescheduled"  # Booking rescheduled
```

### Status Workflow
```
SCHEDULED (Initial)
    ↓
    ├─→ CONFIRMED (Contractor confirmed)
    │       ↓
    │       └─→ COMPLETED (Demo completed)
    │
    └─→ CANCELLED (Booking cancelled)

RESCHEDULED (Moved to different time)
    ↓
    └─→ SCHEDULED (New booking created)
```

---

## Contact Method Enum

### Valid Contact Methods
```python
PHONE = "phone"    # Phone call
EMAIL = "email"    # Email communication
VIDEO = "video"    # Video conference (Zoom)
```

---

## Instance Methods

### Status Check Methods

#### `is_scheduled()`
Check if booking is scheduled.
```python
if booking.is_scheduled():
    print("Booking is scheduled")
```

#### `is_confirmed()`
Check if booking is confirmed.
```python
if booking.is_confirmed():
    print("Contractor confirmed attendance")
```

#### `is_completed()`
Check if booking is completed.
```python
if booking.is_completed():
    print("Demo has been completed")
```

#### `is_cancelled()`
Check if booking is cancelled.
```python
if booking.is_cancelled():
    print("Booking was cancelled")
```

#### `is_rescheduled()`
Check if booking is rescheduled.
```python
if booking.is_rescheduled():
    print("Booking was rescheduled")
```

### Time Check Methods

#### `is_upcoming()`
Check if demo is in the future.
```python
if booking.is_upcoming():
    print("Demo is upcoming")
```

#### `is_past()`
Check if demo is in the past.
```python
if booking.is_past():
    print("Demo has already occurred")
```

### State Check Methods

#### `is_active()`
Check if booking is active (not cancelled or rescheduled).
```python
if booking.is_active():
    print("Booking is active")
```

#### `can_be_confirmed()`
Check if booking can be confirmed.
```python
if booking.can_be_confirmed():
    print("Can confirm this booking")
```

#### `can_be_completed()`
Check if booking can be marked as completed.
```python
if booking.can_be_completed():
    print("Can mark as completed")
```

#### `can_be_cancelled()`
Check if booking can be cancelled.
```python
if booking.can_be_cancelled():
    print("Can cancel this booking")
```

#### `can_be_rescheduled()`
Check if booking can be rescheduled.
```python
if booking.can_be_rescheduled():
    print("Can reschedule this booking")
```

### Display Methods

#### `get_status_display()`
Get human-readable status.
```python
status_text = booking.get_status_display()
# Returns: "Scheduled", "Confirmed", "Completed", etc.
```

#### `get_contact_method_display()`
Get human-readable contact method.
```python
method_text = booking.get_contact_method_display()
# Returns: "Phone", "Email", "Video Call"
```

### Time Calculation Methods

#### `days_until_demo()`
Calculate days until demo.
```python
days = booking.days_until_demo()
if days > 0:
    print(f"Demo in {days} days")
elif days < 0:
    print(f"Demo was {abs(days)} days ago")
```

#### `hours_until_demo()`
Calculate hours until demo.
```python
hours = booking.hours_until_demo()
if hours > 24:
    print(f"Demo in {hours/24:.1f} days")
```

### Conversion Methods

#### `to_dict()`
Convert model to dictionary.
```python
booking_dict = booking.to_dict()
return booking_dict
```

#### `create_from_dict(data)`
Create booking from dictionary.
```python
booking = DemoBooking.create_from_dict({
    "contractor_id": 1,
    "demo_date": datetime(2026, 1, 10, 9, 0),
    "status": "scheduled"
})
```

---

## Class Methods

### Query Methods

#### `get_scheduled_bookings(db_session)`
Get all scheduled bookings.
```python
bookings = DemoBooking.get_scheduled_bookings(db).all()
```

#### `get_upcoming_bookings(db_session)`
Get all upcoming bookings (in the future, not cancelled).
```python
upcoming = DemoBooking.get_upcoming_bookings(db).all()
for booking in upcoming:
    print(f"{booking.contractor.company_name}: {booking.demo_date}")
```

#### `get_past_bookings(db_session)`
Get all past bookings.
```python
past = DemoBooking.get_past_bookings(db).all()
```

#### `get_completed_bookings(db_session)`
Get all completed bookings.
```python
completed = DemoBooking.get_completed_bookings(db).all()
```

#### `get_cancelled_bookings(db_session)`
Get all cancelled bookings.
```python
cancelled = DemoBooking.get_cancelled_bookings(db).all()
```

#### `get_by_contractor(db_session, contractor_id)`
Get all bookings for a contractor.
```python
bookings = DemoBooking.get_by_contractor(db, contractor_id=1).all()
```

#### `get_by_contractor_and_status(db_session, contractor_id, status)`
Get bookings for a contractor with specific status.
```python
scheduled = DemoBooking.get_by_contractor_and_status(
    db, contractor_id=1, status="scheduled"
).all()
```

#### `get_by_date_range(db_session, start_date, end_date)`
Get bookings within a date range.
```python
from datetime import datetime

start = datetime(2026, 1, 1)
end = datetime(2026, 1, 31)
bookings = DemoBooking.get_by_date_range(db, start, end).all()
```

#### `get_conflicting_bookings(db_session, demo_date, duration_minutes)`
Get bookings that conflict with a given time slot.
```python
proposed_time = datetime(2026, 1, 10, 9, 0)
conflicts = DemoBooking.get_conflicting_bookings(db, proposed_time).all()

if conflicts:
    print("Slot is already booked")
```

### Aggregation Methods

#### `count_by_status(db_session)`
Get count of bookings by status.
```python
stats = DemoBooking.count_by_status(db)
print(f"Scheduled: {stats.get('scheduled', 0)}")
print(f"Confirmed: {stats.get('confirmed', 0)}")
print(f"Completed: {stats.get('completed', 0)}")
```

#### `count_upcoming(db_session)`
Count upcoming bookings.
```python
upcoming_count = DemoBooking.count_upcoming(db)
print(f"Upcoming demos: {upcoming_count}")
```

#### `count_by_contractor(db_session, contractor_id)`
Count bookings for a contractor.
```python
count = DemoBooking.count_by_contractor(db, contractor_id=1)
print(f"Bookings for contractor: {count}")
```

---

## Usage Examples

### 1. Create a New Booking
```python
from datetime import datetime

booking = DemoBooking(
    contractor_id=1,
    demo_date=datetime(2026, 1, 10, 9, 0),
    status="scheduled",
    preferred_contact_method="video",
    zoom_link="https://zoom.us/j/123456789"
)
db.add(booking)
db.commit()
```

### 2. Get Upcoming Bookings
```python
upcoming = DemoBooking.get_upcoming_bookings(db).all()
for booking in upcoming:
    print(f"{booking.contractor.company_name}: {booking.demo_date}")
```

### 3. Update Booking Status
```python
booking = db.query(DemoBooking).filter_by(id=1).first()
booking.status = "confirmed"
db.commit()
```

### 4. Check for Slot Conflicts
```python
proposed_time = datetime(2026, 1, 10, 9, 0)
conflicts = DemoBooking.get_conflicting_bookings(db, proposed_time).all()

if conflicts:
    print("Slot is already booked")
else:
    print("Slot is available")
```

### 5. Get Booking Statistics
```python
stats = DemoBooking.count_by_status(db)
print(f"Scheduled: {stats.get('scheduled', 0)}")
print(f"Confirmed: {stats.get('confirmed', 0)}")
print(f"Completed: {stats.get('completed', 0)}")
print(f"Cancelled: {stats.get('cancelled', 0)}")
```

### 6. Filter by Contractor
```python
contractor_bookings = DemoBooking.get_by_contractor(db, contractor_id=1).all()
for booking in contractor_bookings:
    print(f"{booking.status}: {booking.demo_date}")
```

### 7. Get Bookings in Date Range
```python
from datetime import datetime

start = datetime(2026, 1, 1)
end = datetime(2026, 1, 31)
bookings = DemoBooking.get_by_date_range(db, start, end).all()
```

### 8. Check Booking State
```python
booking = db.query(DemoBooking).filter_by(id=1).first()

if booking.is_upcoming():
    print("Demo is upcoming")

if booking.can_be_confirmed():
    print("Demo can be confirmed")

if booking.can_be_rescheduled():
    print("Demo can be rescheduled")
```

### 9. Get Human-Readable Display
```python
booking = db.query(DemoBooking).filter_by(id=1).first()
print(f"Status: {booking.get_status_display()}")
print(f"Contact: {booking.get_contact_method_display()}")
print(f"Days until demo: {booking.days_until_demo()}")
```

### 10. Convert to Dictionary
```python
booking = db.query(DemoBooking).filter_by(id=1).first()
booking_dict = booking.to_dict()
return booking_dict
```

---

## Database Queries

### Get all scheduled bookings
```python
scheduled = db.query(DemoBooking).filter(
    DemoBooking.status == "scheduled"
).all()
```

### Get upcoming bookings
```python
from datetime import datetime

now = datetime.utcnow()
upcoming = db.query(DemoBooking).filter(
    (DemoBooking.demo_date > now) &
    (DemoBooking.status != "cancelled")
).all()
```

### Get bookings for a contractor
```python
bookings = db.query(DemoBooking).filter(
    DemoBooking.contractor_id == 1
).all()
```

### Get bookings by status
```python
confirmed = db.query(DemoBooking).filter(
    DemoBooking.status == "confirmed"
).all()
```

### Count bookings by status
```python
from sqlalchemy import func

status_counts = db.query(
    DemoBooking.status,
    func.count(DemoBooking.id).label("count")
).group_by(DemoBooking.status).all()
```

---

## String Representation

### `__repr__()`
```python
booking = db.query(DemoBooking).first()
print(booking)
# Output: <DemoBooking(id=1, contractor_id=1, demo_date=2026-01-10 09:00:00, status=scheduled)>
```

---

## File Placement

```
app/
├── models/
│   ├── __init__.py
│   ├── contractor.py
│   └── booking.py               # ← This file
├── routes/
├── schemas/
├── database.py
└── main.py
```

---

## Integration with Contractor Model

The DemoBooking model has a Many-to-One relationship with the Contractor model.

**In Contractor model:**
```python
demo_bookings = relationship(
    "DemoBooking",
    back_populates="contractor",
    cascade="all, delete-orphan",
    lazy="select"
)
```

**Usage:**
```python
contractor = db.query(Contractor).first()
for booking in contractor.demo_bookings:
    print(f"{booking.status}: {booking.demo_date}")
```

---

## Summary

The `DemoBooking` model provides:

✅ **Complete booking information** - Date, time, status, contact method
✅ **Relationship management** - Links to Contractor
✅ **Status tracking** - Lifecycle management
✅ **Time calculations** - Days/hours until demo
✅ **State checking** - Can be confirmed/cancelled/rescheduled
✅ **Query methods** - Common queries as class methods
✅ **Aggregation methods** - Statistics and counts
✅ **Display methods** - Human-readable output
✅ **Conversion methods** - To/from dictionary
✅ **Comprehensive indexing** - Performance optimization
✅ **Cascade delete** - Data integrity
✅ **Timestamps** - Audit trail

Everything is production-ready and fully documented!
