# app/routes/booking.py - Demo Booking Routes Guide

## Overview

The `app/routes/booking.py` module handles demo scheduling and booking management.

**Purpose:**
- Generate available demo time slots
- Schedule demo appointments
- Manage booking status
- Send confirmation emails
- Track booking statistics
- Prevent double-booking

---

## Demo Scheduling Rules

### Time Slots
- **Duration:** 30 minutes per slot
- **Business Hours:** 9 AM - 5 PM
- **Days:** Weekdays only (Monday-Friday)
- **Timezone:** America/New_York (EST)
- **Available Period:** Next 14 days

### Example Slots
```
2026-01-10 (Friday)
- 09:00 - 09:30
- 09:30 - 10:00
- 10:00 - 10:30
... (continues until 4:30 PM)
```

---

## Endpoints

### 1. Get Available Slots

**Endpoint:** `GET /api/booking/available-slots`

**Response:**
```json
{
    "total_slots": 112,
    "slots": [
        {
            "slot_id": "2026-01-10-09:00",
            "date": "2026-01-10",
            "start_time": "09:00",
            "end_time": "09:30",
            "available": true
        },
        {
            "slot_id": "2026-01-10-09:30",
            "date": "2026-01-10",
            "start_time": "09:30",
            "end_time": "10:00",
            "available": false
        }
    ],
    "timezone": "America/New_York",
    "business_hours": "9 AM - 5 PM (Weekdays)"
}
```

**Features:**
- ✅ Generates 30-minute slots
- ✅ Checks for conflicts
- ✅ Marks unavailable slots
- ✅ Returns timezone information
- ✅ No authentication required

**Example:**
```bash
curl http://localhost:8000/api/booking/available-slots
```

---

### 2. Schedule Demo

**Endpoint:** `POST /api/booking/schedule-demo`

**Status Code:** 201 Created

**Request:**
```json
{
    "email": "john@abcconstruction.com",
    "slot_id": "2026-01-10-09:00",
    "preferred_contact_method": "video",
    "notes": "Interested in project scheduling features"
}
```

**Response:**
```json
{
    "id": 1,
    "contractor_id": 1,
    "email": "john@abcconstruction.com",
    "company_name": "ABC Construction",
    "contact_name": "John Smith",
    "demo_date": "2026-01-10T09:00:00",
    "demo_time": "09:00",
    "status": "scheduled",
    "preferred_contact_method": "video",
    "notes": "Interested in project scheduling features",
    "zoom_link": "https://zoom.us/j/1202601100900",
    "confirmation_sent": false,
    "created_at": "2026-01-05T10:30:00",
    "updated_at": "2026-01-05T10:30:00"
}
```

**Features:**
- ✅ Validates contractor email
- ✅ Checks slot availability
- ✅ Prevents double-booking
- ✅ Creates booking record
- ✅ Generates Zoom link
- ✅ Sends confirmation email asynchronously
- ✅ Updates contractor demo flags

**Error Codes:**
- 404: Contractor not found
- 409: Slot already booked
- 400: Invalid slot ID
- 422: Validation error
- 500: Database error

**Example:**
```bash
curl -X POST http://localhost:8000/api/booking/schedule-demo \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@abcconstruction.com",
    "slot_id": "2026-01-10-09:00",
    "preferred_contact_method": "video"
  }'
```

---

### 3. List Bookings

**Endpoint:** `GET /api/booking/bookings`

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 10, max: 100)
- `status_filter`: Filter by status (scheduled, confirmed, completed, cancelled)
- `email`: Filter by contractor email

**Response:**
```json
{
    "total": 42,
    "count": 10,
    "page": 1,
    "page_size": 10,
    "bookings": [
        {
            "id": 1,
            "contractor_id": 1,
            "email": "john@abcconstruction.com",
            "company_name": "ABC Construction",
            "contact_name": "John Smith",
            "demo_date": "2026-01-10T09:00:00",
            "demo_time": "09:00",
            "status": "scheduled",
            "preferred_contact_method": "video",
            "notes": "Interested in project scheduling",
            "zoom_link": "https://zoom.us/j/1202601100900",
            "confirmation_sent": true,
            "created_at": "2026-01-05T10:30:00",
            "updated_at": "2026-01-05T10:30:00"
        }
    ]
}
```

**Example:**
```bash
# Get first page
curl http://localhost:8000/api/booking/bookings

# Filter by status
curl http://localhost:8000/api/booking/bookings?status_filter=scheduled

# Filter by email
curl http://localhost:8000/api/booking/bookings?email=john@abcconstruction.com
```

---

### 4. Get Booking by ID

**Endpoint:** `GET /api/booking/bookings/{booking_id}`

**Response:** DemoBookingResponse (same as list items)

**Error Codes:**
- 404: Booking not found
- 500: Database error

**Example:**
```bash
curl http://localhost:8000/api/booking/bookings/1
```

---

### 5. Update Booking Status

**Endpoint:** `PUT /api/booking/bookings/{booking_id}`

**Request:**
```json
{
    "status": "confirmed",
    "notes": "Contractor confirmed attendance"
}
```

**Valid Statuses:**
- `scheduled` - Initial booking
- `confirmed` - Contractor confirmed
- `completed` - Demo completed
- `cancelled` - Booking cancelled
- `rescheduled` - Booking rescheduled

**Response:** DemoBookingResponse (updated)

**Error Codes:**
- 404: Booking not found
- 400: Invalid status
- 500: Database error

**Example:**
```bash
curl -X PUT http://localhost:8000/api/booking/bookings/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "confirmed"}'
```

---

### 6. Cancel Booking

**Endpoint:** `DELETE /api/booking/bookings/{booking_id}`

**Status Code:** 204 No Content

**Error Codes:**
- 404: Booking not found
- 500: Database error

**Example:**
```bash
curl -X DELETE http://localhost:8000/api/booking/bookings/1
```

---

### 7. Get Booking Statistics

**Endpoint:** `GET /api/booking/stats`

**Response:**
```json
{
    "total_bookings": 42,
    "scheduled": 15,
    "confirmed": 12,
    "completed": 10,
    "cancelled": 5,
    "rescheduled": 0,
    "avg_bookings_per_day": 2.1,
    "upcoming_bookings": 27,
    "past_bookings": 15
}
```

**Example:**
```bash
curl http://localhost:8000/api/booking/stats
```

---

## BookingManager Class

### Purpose
Encapsulates booking logic for slot generation and availability checking.

### Methods

#### `generate_available_slots(db)`
Generate available demo slots for the next 14 days.

**Returns:**
List of slot dictionaries with:
- slot_id, date, start_time, end_time
- available (boolean)
- datetime (datetime object)

**Features:**
- ✅ Generates 30-minute slots
- ✅ Weekdays only (Mon-Fri)
- ✅ 9 AM - 5 PM hours
- ✅ Checks for conflicts
- ✅ Marks unavailable slots

#### `parse_slot_id(slot_id)`
Parse slot ID to datetime.

**Parameters:**
- slot_id: Slot ID in format "YYYY-MM-DD-HH:MM"

**Returns:**
Datetime object

**Raises:**
- ValueError: If slot ID format is invalid

#### `is_slot_available(slot_id, db)`
Check if a slot is available for booking.

**Parameters:**
- slot_id: Slot ID to check
- db: Database session

**Returns:**
True if available, False otherwise

---

## Database Models Used

### DemoBooking Model
Stores demo booking information:
- contractor_id (foreign key)
- demo_date (datetime)
- status (scheduled, confirmed, completed, cancelled, rescheduled)
- preferred_contact_method (phone, email, video)
- notes
- zoom_link
- confirmation_sent flag
- created_at, updated_at

### Contractor Model
Updated with:
- demo_scheduled (boolean)
- demo_date (datetime)
- demo_completed (boolean)

---

## Data Flow

### Schedule Demo Process

```
1. User requests available slots
   ↓
2. Generate 30-minute slots for next 14 days
   ↓
3. Check each slot for conflicts
   ↓
4. Mark available/unavailable
   ↓
5. Return slot list to user
   ↓
6. User selects slot and submits booking
   ↓
7. Validate contractor email
   ├─ NOT FOUND: Return 404
   └─ FOUND: Continue
   ↓
8. Parse and validate slot ID
   ├─ INVALID: Return 400
   └─ VALID: Continue
   ↓
9. Check slot availability
   ├─ BOOKED: Return 409 Conflict
   └─ AVAILABLE: Continue
   ↓
10. Generate Zoom link
    ↓
11. Create DemoBooking record
    ↓
12. Update contractor flags
    ├─ demo_scheduled = true
    ├─ demo_date = slot_datetime
    └─ demo_completed = false
    ↓
13. Commit to database
    ↓
14. Queue confirmation email (background task)
    ↓
15. Return booking response (201 Created)
```

---

## Schemas

### TimeSlot
**Purpose:** Represent available time slot

**Fields:**
- slot_id, date, start_time, end_time
- available (boolean)

### AvailableSlotsResponse
**Purpose:** Return available slots

**Fields:**
- total_slots, slots (list of TimeSlot)
- timezone, business_hours

### ScheduleDemoRequest
**Purpose:** Validate booking request

**Fields:**
- email (required)
- slot_id (required)
- preferred_contact_method (optional: phone, email, video)
- notes (optional, max 500 chars)

### DemoBookingResponse
**Purpose:** Return booking details

**Fields:**
- id, contractor_id, email, company_name, contact_name
- demo_date, demo_time, status
- preferred_contact_method, notes, zoom_link
- confirmation_sent, created_at, updated_at

### BookingListResponse
**Purpose:** Return paginated list

**Fields:**
- total, count, page, page_size
- bookings (list of DemoBookingResponse)

### BookingStatusUpdate
**Purpose:** Update booking status

**Fields:**
- status (required: scheduled, confirmed, completed, cancelled, rescheduled)
- notes (optional, max 500 chars)

### BookingStatsResponse
**Purpose:** Return statistics

**Fields:**
- total_bookings, scheduled, confirmed, completed, cancelled, rescheduled
- avg_bookings_per_day, upcoming_bookings, past_bookings

---

## Booking Status Workflow

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

## Constants

| Constant | Value | Purpose |
|----------|-------|---------|
| DEMO_DURATION_MINUTES | 30 | Length of each demo slot |
| BUSINESS_HOURS_START | 9 | Start of business hours (9 AM) |
| BUSINESS_HOURS_END | 17 | End of business hours (5 PM) |
| AVAILABLE_DAYS_AHEAD | 14 | Number of days to show slots |
| TIMEZONE | America/New_York | Timezone for scheduling |

---

## Error Handling

### Slot Not Available (409 Conflict)
```json
{
    "detail": "Selected time slot is no longer available. Please choose another slot."
}
```

### Contractor Not Found (404)
```json
{
    "detail": "Contractor with email 'john@abcconstruction.com' not found"
}
```

### Invalid Slot ID (400)
```json
{
    "detail": "Invalid slot ID format: time data does not match format"
}
```

### Invalid Status (400)
```json
{
    "detail": "Invalid status. Must be one of: scheduled, confirmed, completed, cancelled, rescheduled"
}
```

### Booking Not Found (404)
```json
{
    "detail": "Booking with id 999 not found"
}
```

### Database Error (500)
```json
{
    "detail": "Failed to schedule demo"
}
```

---

## Integration with main.py

```python
from app.routes import booking

app.include_router(booking.router, tags=["booking"])
```

---

## Testing Workflow

### 1. Get Available Slots
```bash
curl http://localhost:8000/api/booking/available-slots
```

### 2. Schedule Demo
```bash
curl -X POST http://localhost:8000/api/booking/schedule-demo \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@abcconstruction.com",
    "slot_id": "2026-01-10-09:00",
    "preferred_contact_method": "video"
  }'
```

### 3. List Bookings
```bash
curl http://localhost:8000/api/booking/bookings
```

### 4. Update Booking Status
```bash
curl -X PUT http://localhost:8000/api/booking/bookings/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "confirmed"}'
```

### 5. Get Statistics
```bash
curl http://localhost:8000/api/booking/stats
```

---

## Database Queries

### Get all scheduled bookings
```python
bookings = db.query(DemoBooking).filter(
    DemoBooking.status == "scheduled"
).all()
```

### Get upcoming bookings
```python
now = datetime.utcnow()
upcoming = db.query(DemoBooking).filter(
    and_(
        DemoBooking.demo_date > now,
        DemoBooking.status != "cancelled"
    )
).all()
```

### Get bookings for a contractor
```python
bookings = db.query(DemoBooking).filter(
    DemoBooking.contractor_id == contractor_id
).all()
```

### Get booking statistics
```python
total = db.query(func.count(DemoBooking.id)).scalar()
scheduled = db.query(func.count(DemoBooking.id)).filter(
    DemoBooking.status == "scheduled"
).scalar()
```

---

## File Placement

```
app/
├── routes/
│   ├── __init__.py
│   ├── forms.py
│   ├── roi.py
│   ├── booking.py               # ← This file
│   └── contractor.py
├── models/
│   └── contractor.py
├── config.py
├── database.py
└── main.py
```

---

## Summary

The `app/routes/booking.py` module provides:

✅ **Slot generation** - 30-minute slots for next 14 days
✅ **Availability checking** - Prevent double-booking
✅ **Demo scheduling** - Book appointments
✅ **Status management** - Track booking lifecycle
✅ **Email automation** - Send confirmations
✅ **Statistics** - Aggregated booking data
✅ **Filtering & pagination** - List bookings
✅ **Error handling** - Detailed error responses
✅ **Logging** - Detailed operation logging
✅ **Database integration** - Full SQLAlchemy integration
✅ **Timezone support** - EST timezone handling
✅ **Background tasks** - Non-blocking email sending

Everything is production-ready and fully documented!
