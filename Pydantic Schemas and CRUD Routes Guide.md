# Pydantic Schemas and CRUD Routes Guide

## Overview

This guide covers the Pydantic schemas and FastAPI CRUD routes for the Contractor model:

1. **Schemas** (`app/schemas/contractor.py`) - Request/response validation
2. **Routes** (`app/routes/contractor.py`) - CRUD endpoints

---

## Part 1: Pydantic Schemas

### Purpose

Pydantic schemas provide:
- Request validation (incoming data)
- Response serialization (outgoing data)
- Type checking and conversion
- Documentation for API clients
- Example data for Swagger UI

### File Location

```
app/
├── schemas/
│   ├── __init__.py
│   └── contractor.py          # ← This file
```

---

## Schema Hierarchy

```
BaseModel (Pydantic)
    ↓
ContractorBase
    ├── ContractorCreate (inherits from ContractorBase)
    └── ContractorUpdate (standalone)
    
ContractorResponse (inherits from ContractorBase)
ContractorListResponse
ContractorStatistics
ErrorResponse
```

---

## Schema Details

### 1. ContractorBase

**Purpose:** Base schema with common fields

**Fields:**
```python
company_name: str              # Required, 2-255 chars
contact_name: str              # Required, 2-255 chars
email: EmailStr                # Required, unique
phone: Optional[str]           # Optional, max 20 chars
company_size: Optional[str]    # small, medium, large
annual_revenue: Optional[float] # >= 0
current_challenges: Optional[str] # max 2000 chars
industry_focus: Optional[str]  # commercial, residential, mixed
```

**Validators:**
- `company_size` - Must be small, medium, or large
- `industry_focus` - Must be commercial, residential, or mixed

---

### 2. ContractorCreate

**Purpose:** Schema for creating contractors

**Inherits from:** ContractorBase

**Usage:**
```python
@app.post("/contractors")
async def create_contractor(contractor: ContractorCreate):
    # contractor is validated against ContractorCreate schema
    ...
```

**Example Request:**
```json
{
    "company_name": "ABC Construction",
    "contact_name": "John Smith",
    "email": "john@abcconstruction.com",
    "phone": "404-555-0123",
    "company_size": "medium",
    "annual_revenue": 5000000,
    "current_challenges": "Schedule delays and subcontractor coordination",
    "industry_focus": "commercial"
}
```

---

### 3. ContractorUpdate

**Purpose:** Schema for updating contractors

**All fields are optional** - only provided fields will be updated

**Fields:**
```python
company_name: Optional[str]
contact_name: Optional[str]
email: Optional[EmailStr]
phone: Optional[str]
company_size: Optional[str]
annual_revenue: Optional[float]
current_challenges: Optional[str]
industry_focus: Optional[str]
estimated_annual_savings: Optional[float]
roi_percentage: Optional[float]
payback_period_months: Optional[float]
demo_scheduled: Optional[bool]
demo_date: Optional[datetime]
demo_completed: Optional[bool]
conversion_status: Optional[str]
notes: Optional[str]
```

**Validators:**
- `company_size` - Must be small, medium, or large
- `industry_focus` - Must be commercial, residential, or mixed
- `conversion_status` - Must be lead, prospect, customer, or lost

**Example Request:**
```json
{
    "conversion_status": "prospect",
    "demo_scheduled": true,
    "estimated_annual_savings": 1000000,
    "roi_percentage": 200
}
```

---

### 4. ContractorResponse

**Purpose:** Schema for API responses

**Inherits from:** ContractorBase

**Additional Fields:**
```python
id: int                           # Contractor ID
estimated_annual_savings: Optional[float]
roi_percentage: Optional[float]
payback_period_months: Optional[float]
demo_scheduled: bool
demo_date: Optional[datetime]
demo_completed: bool
conversion_status: str
welcome_email_sent: bool
roi_report_sent: bool
last_email_sent_at: Optional[datetime]
notes: Optional[str]
created_at: datetime
updated_at: datetime
```

**Configuration:**
```python
class Config:
    from_attributes = True  # Convert SQLAlchemy models to Pydantic
    json_schema_extra = {
        "example": { ... }  # Example data for Swagger UI
    }
```

**Example Response:**
```json
{
    "id": 1,
    "company_name": "ABC Construction",
    "contact_name": "John Smith",
    "email": "john@abcconstruction.com",
    "phone": "404-555-0123",
    "company_size": "medium",
    "annual_revenue": 5000000,
    "current_challenges": "Schedule delays and subcontractor coordination",
    "industry_focus": "commercial",
    "estimated_annual_savings": 1000000,
    "roi_percentage": 200,
    "payback_period_months": 0.06,
    "demo_scheduled": true,
    "demo_date": "2026-01-10T14:00:00",
    "demo_completed": false,
    "conversion_status": "prospect",
    "welcome_email_sent": true,
    "roi_report_sent": false,
    "created_at": "2026-01-05T10:00:00",
    "updated_at": "2026-01-05T10:30:00"
}
```

---

### 5. ContractorListResponse

**Purpose:** Schema for paginated list responses

**Fields:**
```python
total: int              # Total number of contractors
count: int              # Number in this response
page: int               # Current page number
page_size: int          # Items per page
contractors: List[ContractorResponse]  # List of contractors
```

**Example Response:**
```json
{
    "total": 42,
    "count": 10,
    "page": 1,
    "page_size": 10,
    "contractors": [
        {
            "id": 1,
            "company_name": "ABC Construction",
            ...
        },
        {
            "id": 2,
            "company_name": "XYZ Contractors",
            ...
        }
    ]
}
```

---

### 6. ContractorStatistics

**Purpose:** Schema for statistics endpoint

**Fields:**
```python
total_contractors: int
leads: int
prospects: int
customers: int
lost: int
demos_scheduled: int
demos_completed: int
avg_estimated_savings: Optional[float]
avg_roi_percentage: Optional[float]
total_potential_savings: Optional[float]
```

**Example Response:**
```json
{
    "total_contractors": 42,
    "leads": 20,
    "prospects": 15,
    "customers": 5,
    "lost": 2,
    "demos_scheduled": 8,
    "demos_completed": 3,
    "avg_estimated_savings": 1000000,
    "avg_roi_percentage": 200,
    "total_potential_savings": 42000000
}
```

---

### 7. ErrorResponse

**Purpose:** Schema for error responses

**Fields:**
```python
status: str             # Error status
message: str            # Error message
error: Optional[str]    # Detailed error info
```

**Example Response:**
```json
{
    "status": "error",
    "message": "Contractor not found",
    "error": "No contractor with id=999"
}
```

---

## Part 2: CRUD Routes

### Purpose

Routes provide HTTP endpoints for CRUD operations on contractors.

### File Location

```
app/
├── routes/
│   ├── __init__.py
│   ├── forms.py
│   ├── roi.py
│   ├── booking.py
│   └── contractor.py          # ← This file
```

### Router Configuration

```python
router = APIRouter(
    prefix="/api/contractors",
    tags=["contractors"],
    responses={
        404: {"model": ErrorResponse},
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
```

---

## Endpoint Reference

### 1. Create Contractor

**Endpoint:** `POST /api/contractors`

**Status Code:** 201 Created

**Request:**
```json
{
    "company_name": "ABC Construction",
    "contact_name": "John Smith",
    "email": "john@abcconstruction.com",
    "phone": "404-555-0123",
    "company_size": "medium",
    "annual_revenue": 5000000,
    "current_challenges": "Schedule delays"
}
```

**Response:** ContractorResponse

**Error Codes:**
- 400: Email already exists
- 422: Validation error
- 500: Database error

**Example:**
```bash
curl -X POST http://localhost:8000/api/contractors \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "ABC Construction",
    "contact_name": "John Smith",
    "email": "john@abcconstruction.com",
    "phone": "404-555-0123",
    "company_size": "medium"
  }'
```

---

### 2. List Contractors

**Endpoint:** `GET /api/contractors`

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 10, max: 100)
- `company_size`: Filter by size
- `conversion_status`: Filter by status
- `demo_scheduled`: Filter by demo scheduled
- `search`: Search by company name or email

**Response:** ContractorListResponse

**Example:**
```bash
# Get first page
curl http://localhost:8000/api/contractors

# Get page 2 with 20 items
curl http://localhost:8000/api/contractors?page=2&page_size=20

# Filter by company size
curl http://localhost:8000/api/contractors?company_size=medium

# Filter by status
curl http://localhost:8000/api/contractors?conversion_status=prospect

# Search
curl http://localhost:8000/api/contractors?search=ABC
```

---

### 3. Get Contractor by ID

**Endpoint:** `GET /api/contractors/{contractor_id}`

**Path Parameters:**
- `contractor_id`: Contractor ID

**Response:** ContractorResponse

**Error Codes:**
- 404: Contractor not found
- 500: Database error

**Example:**
```bash
curl http://localhost:8000/api/contractors/1
```

---

### 4. Get Contractor by Email

**Endpoint:** `GET /api/contractors/by-email/{email}`

**Path Parameters:**
- `email`: Contractor email address

**Response:** ContractorResponse

**Error Codes:**
- 404: Contractor not found
- 500: Database error

**Example:**
```bash
curl http://localhost:8000/api/contractors/by-email/john@abcconstruction.com
```

---

### 5. Get Contractors by Status

**Endpoint:** `GET /api/contractors/by-status/{status}`

**Path Parameters:**
- `status`: Conversion status (lead, prospect, customer, lost)

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 10)

**Response:** ContractorListResponse

**Error Codes:**
- 400: Invalid status
- 500: Database error

**Example:**
```bash
curl http://localhost:8000/api/contractors/by-status/prospect
curl http://localhost:8000/api/contractors/by-status/customer?page=1&page_size=20
```

---

### 6. Update Contractor

**Endpoint:** `PUT /api/contractors/{contractor_id}`

**Path Parameters:**
- `contractor_id`: Contractor ID

**Request:** ContractorUpdate (all fields optional)

**Response:** ContractorResponse

**Error Codes:**
- 404: Contractor not found
- 400: Email already exists
- 422: Validation error
- 500: Database error

**Example:**
```bash
curl -X PUT http://localhost:8000/api/contractors/1 \
  -H "Content-Type: application/json" \
  -d '{
    "conversion_status": "prospect",
    "demo_scheduled": true,
    "estimated_annual_savings": 1000000
  }'
```

---

### 7. Delete Contractor

**Endpoint:** `DELETE /api/contractors/{contractor_id}`

**Path Parameters:**
- `contractor_id`: Contractor ID

**Status Code:** 204 No Content

**Error Codes:**
- 404: Contractor not found
- 500: Database error

**Note:** Deletes contractor and all related records (cascade delete)

**Example:**
```bash
curl -X DELETE http://localhost:8000/api/contractors/1
```

---

### 8. Get Statistics

**Endpoint:** `GET /api/contractors/stats/overview`

**Response:** ContractorStatistics

**Example:**
```bash
curl http://localhost:8000/api/contractors/stats/overview
```

**Response:**
```json
{
    "total_contractors": 42,
    "leads": 20,
    "prospects": 15,
    "customers": 5,
    "lost": 2,
    "demos_scheduled": 8,
    "demos_completed": 3,
    "avg_estimated_savings": 1000000,
    "avg_roi_percentage": 200,
    "total_potential_savings": 42000000
}
```

---

## Complete Endpoint Summary

| Method | Endpoint | Purpose | Status |
|--------|----------|---------|--------|
| POST | `/api/contractors` | Create contractor | 201 |
| GET | `/api/contractors` | List contractors | 200 |
| GET | `/api/contractors/{id}` | Get by ID | 200 |
| GET | `/api/contractors/by-email/{email}` | Get by email | 200 |
| GET | `/api/contractors/by-status/{status}` | Get by status | 200 |
| PUT | `/api/contractors/{id}` | Update contractor | 200 |
| DELETE | `/api/contractors/{id}` | Delete contractor | 204 |
| GET | `/api/contractors/stats/overview` | Get statistics | 200 |

---

## Usage in FastAPI Application

### 1. Import Router

```python
from app.routes.contractor import router

app.include_router(router)
```

### 2. Use in main.py

```python
from app.routes import contractor

app.include_router(contractor.router, tags=["contractors"])
```

### 3. Access API Documentation

- **Swagger UI:** http://localhost:8000/api/docs
- **ReDoc:** http://localhost:8000/api/redoc

---

## Common Workflows

### Create and List Contractors

```bash
# Create contractor
curl -X POST http://localhost:8000/api/contractors \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "ABC Construction",
    "contact_name": "John Smith",
    "email": "john@abcconstruction.com",
    "phone": "404-555-0123",
    "company_size": "medium"
  }'

# List all contractors
curl http://localhost:8000/api/contractors

# List prospects only
curl http://localhost:8000/api/contractors?conversion_status=prospect
```

### Update Contractor Status

```bash
# Get contractor
curl http://localhost:8000/api/contractors/1

# Update status to prospect
curl -X PUT http://localhost:8000/api/contractors/1 \
  -H "Content-Type: application/json" \
  -d '{"conversion_status": "prospect"}'
```

### Get Statistics

```bash
curl http://localhost:8000/api/contractors/stats/overview
```

---

## Error Handling

### Validation Errors (422)

```json
{
    "detail": [
        {
            "loc": ["body", "company_name"],
            "msg": "ensure this value has at least 2 characters",
            "type": "value_error.string.too_short"
        }
    ]
}
```

### Not Found (404)

```json
{
    "detail": "Contractor with id 999 not found"
}
```

### Duplicate Email (400)

```json
{
    "detail": "Contractor with email 'john@abcconstruction.com' already exists"
}
```

---

## File Placement

```
app/
├── __init__.py
├── schemas/
│   ├── __init__.py
│   └── contractor.py          # Pydantic schemas
├── routes/
│   ├── __init__.py
│   ├── forms.py
│   ├── roi.py
│   ├── booking.py
│   └── contractor.py          # CRUD routes
├── models/
│   └── contractor.py
├── database.py
├── main.py
└── ...
```

---

## Summary

**Schemas provide:**
✅ Request validation
✅ Response serialization
✅ Type checking
✅ API documentation
✅ Example data

**Routes provide:**
✅ Full CRUD operations
✅ Pagination and filtering
✅ Search functionality
✅ Statistics endpoint
✅ Comprehensive error handling
✅ Database dependency injection

Everything is production-ready and fully documented!
