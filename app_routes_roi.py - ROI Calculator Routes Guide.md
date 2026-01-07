# app/routes/roi.py - ROI Calculator Routes Guide

## Overview

The `app/routes/roi.py` module handles ROI calculations for construction contractors.

**Purpose:**
- Calculate ROI based on project and delay data
- Save calculations to database
- Update contractor with ROI metrics
- Send ROI reports via email
- Provide ROI statistics and summaries

---

## ROI Calculation Formula

### Annual Delay Cost
```
Annual Delay Cost = Annual Delayed Projects × Average Delay Days × Cost Per Day
Annual Delayed Projects = (Delay Percentage / 100) × Projects Per Year
```

### Estimated Annual Savings
```
Estimated Annual Savings = (Annual Delay Cost × Delay Reduction %) - AI Solution Cost
```

### Payback Period
```
Payback Period (months) = AI Solution Cost / Monthly Savings
Monthly Savings = Estimated Annual Savings / 12
```

### ROI Percentage
```
ROI % = (Estimated Annual Savings / AI Solution Cost) × 100
```

### Break-Even Point
```
Break-Even (months) = AI Solution Cost / Monthly Savings
```

---

## Default Constants

From `app/config.py`:
- **Cost Per Day Delay:** $45,662
- **AI Solution Annual Cost:** $5,000
- **Delay Reduction Percentage:** 65% (0.65)
- **Average Project Duration:** 37 days

---

## Endpoints

### 1. Calculate ROI

**Endpoint:** `POST /api/roi/calculate`

**Status Code:** 201 Created

**Request Body:**
```json
{
    "email": "john@abcconstruction.com",
    "project_value": 500000,
    "delay_percentage": 75,
    "projects_per_year": 4,
    "avg_delay_days": 37,
    "company_size": "medium",
    "industry_focus": "commercial"
}
```

**Response:**
```json
{
    "id": 1,
    "contractor_id": 1,
    "email": "john@abcconstruction.com",
    "project_value": 500000,
    "delay_percentage": 75,
    "projects_per_year": 4,
    "avg_delay_days": 37,
    "financial_metrics": {
        "annual_delay_cost": 1369860,
        "annual_delayed_projects": 3,
        "estimated_annual_savings": 885441,
        "monthly_savings": 73787,
        "ai_solution_annual_cost": 5000,
        "net_annual_benefit": 885441,
        "payback_period_months": 0.07,
        "roi_percentage": 17609,
        "break_even_months": 0.07
    },
    "calculation_date": "2026-01-05T10:30:00",
    "created_at": "2026-01-05T10:30:00"
}
```

**Features:**
- ✅ Validates input data
- ✅ Performs detailed ROI calculations
- ✅ Saves calculation to database
- ✅ Updates contractor with ROI data
- ✅ Sends ROI report email asynchronously
- ✅ Returns comprehensive financial metrics

**Error Codes:**
- 404: Contractor not found
- 400: Invalid data
- 422: Validation error
- 500: Database error

**Example:**
```bash
curl -X POST http://localhost:8000/api/roi/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@abcconstruction.com",
    "project_value": 500000,
    "delay_percentage": 75,
    "projects_per_year": 4
  }'
```

---

### 2. Get ROI Summary

**Endpoint:** `GET /api/roi/roi-summary/{email}`

**Response:**
```json
{
    "contractor_id": 1,
    "email": "john@abcconstruction.com",
    "company_name": "ABC Construction",
    "estimated_annual_savings": 885441,
    "roi_percentage": 17609,
    "payback_period_months": 0.07,
    "last_calculation_date": "2026-01-05T10:30:00",
    "calculation_count": 1
}
```

**Features:**
- ✅ Returns most recent ROI calculation
- ✅ Includes contractor information
- ✅ Shows calculation count
- ✅ Quick summary for dashboard

**Error Codes:**
- 404: Contractor or calculation not found
- 500: Database error

**Example:**
```bash
curl http://localhost:8000/api/roi/roi-summary/john@abcconstruction.com
```

---

### 3. List Calculations

**Endpoint:** `GET /api/roi/calculations`

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 10, max: 100)
- `email`: Filter by contractor email

**Response:**
```json
{
    "total": 42,
    "count": 10,
    "page": 1,
    "page_size": 10,
    "calculations": [
        {
            "id": 1,
            "contractor_id": 1,
            "email": "john@abcconstruction.com",
            "project_value": 500000,
            "delay_percentage": 75,
            "projects_per_year": 4,
            "avg_delay_days": 37,
            "financial_metrics": { ... },
            "calculation_date": "2026-01-05T10:30:00",
            "created_at": "2026-01-05T10:30:00"
        }
    ]
}
```

**Example:**
```bash
# Get first page
curl http://localhost:8000/api/roi/calculations

# Filter by email
curl http://localhost:8000/api/roi/calculations?email=john@abcconstruction.com

# Get page 2 with 20 items
curl http://localhost:8000/api/roi/calculations?page=2&page_size=20
```

---

### 4. Get Calculation by ID

**Endpoint:** `GET /api/roi/calculations/{calculation_id}`

**Response:** ROICalculationResponse (same as list items)

**Error Codes:**
- 404: Calculation not found
- 500: Database error

**Example:**
```bash
curl http://localhost:8000/api/roi/calculations/1
```

---

### 5. Get ROI Statistics

**Endpoint:** `GET /api/roi/stats`

**Response:**
```json
{
    "total_calculations": 42,
    "avg_estimated_savings": 885441,
    "avg_roi_percentage": 17609,
    "total_potential_savings": 37188522,
    "contractors_with_roi": 42,
    "avg_payback_period_months": 0.07,
    "highest_roi_percentage": 25000,
    "lowest_roi_percentage": 5000
}
```

**Features:**
- ✅ Total calculations count
- ✅ Average and total savings
- ✅ Average ROI percentage
- ✅ Number of contractors with ROI
- ✅ Payback period statistics
- ✅ Highest and lowest ROI

**Example:**
```bash
curl http://localhost:8000/api/roi/stats
```

---

## ROI Calculator Class

### Purpose
Encapsulates ROI calculation logic with industry-standard formulas.

### Methods

#### `__init__(settings)`
Initialize calculator with application settings.

**Parameters:**
- settings: Application settings with ROI constants

#### `calculate(project_value, delay_percentage, projects_per_year, avg_delay_days)`
Calculate ROI metrics.

**Parameters:**
- project_value: Average project value (required, > 0)
- delay_percentage: % of projects with delays (required, 0-100)
- projects_per_year: Number of projects per year (required, > 0)
- avg_delay_days: Average delay in days (optional, default: 37)

**Returns:**
Dictionary with financial metrics:
- annual_delay_cost
- annual_delayed_projects
- estimated_annual_savings
- monthly_savings
- ai_solution_annual_cost
- net_annual_benefit
- payback_period_months
- roi_percentage
- break_even_months

**Raises:**
- ValueError: If inputs are invalid

---

## Database Models Used

### ROICalculation Model
Stores ROI calculations:
- contractor_id (foreign key)
- project_value, delay_percentage, projects_per_year
- avg_delay_days
- Financial metrics (savings, ROI, payback period, etc.)
- calculation_date, created_at

### Contractor Model
Updated with:
- estimated_annual_savings
- roi_percentage
- payback_period_months
- roi_report_sent flag
- last_email_sent_at

---

## Data Flow

### ROI Calculation Process

```
1. User submits ROI calculation
   ↓
2. Validate request data
   ↓
3. Get contractor by email
   ├─ NOT FOUND: Return 404
   └─ FOUND: Continue
   ↓
4. Initialize ROI calculator
   ↓
5. Validate calculation parameters
   ├─ INVALID: Return 400
   └─ VALID: Continue
   ↓
6. Perform ROI calculations
   ├─ Calculate annual delay cost
   ├─ Calculate estimated savings
   ├─ Calculate payback period
   ├─ Calculate ROI percentage
   └─ Calculate break-even point
   ↓
7. Create ROICalculation record
   ↓
8. Update contractor with ROI data
   ├─ Set estimated_annual_savings
   ├─ Set roi_percentage
   ├─ Set payback_period_months
   ├─ Set roi_report_sent = true
   └─ Set last_email_sent_at
   ↓
9. Commit to database
   ↓
10. Queue ROI report email (background task)
    ↓
11. Return calculation response (201 Created)
```

---

## Schemas

### ROICalculationRequest
**Purpose:** Validate incoming calculation request

**Fields:**
- email (required, valid email)
- project_value (required, > 0)
- delay_percentage (required, 0-100)
- projects_per_year (required, > 0)
- avg_delay_days (optional, >= 0, default: 37)
- company_size (optional)
- industry_focus (optional)

### FinancialMetrics
**Purpose:** Return financial metrics

**Fields:**
- annual_delay_cost
- annual_delayed_projects
- estimated_annual_savings
- monthly_savings
- ai_solution_annual_cost
- net_annual_benefit
- payback_period_months
- roi_percentage
- break_even_months

### ROICalculationResponse
**Purpose:** Return calculation with metrics

**Fields:**
- id, contractor_id, email
- project_value, delay_percentage, projects_per_year, avg_delay_days
- financial_metrics (FinancialMetrics)
- calculation_date, created_at

### ROISummaryResponse
**Purpose:** Return quick ROI summary

**Fields:**
- contractor_id, email, company_name
- estimated_annual_savings, roi_percentage, payback_period_months
- last_calculation_date, calculation_count

### ROICalculationListResponse
**Purpose:** Return paginated list

**Fields:**
- total, count, page, page_size
- calculations (list of ROICalculationResponse)

### ROIStatsResponse
**Purpose:** Return statistics

**Fields:**
- total_calculations, contractors_with_roi
- avg_estimated_savings, avg_roi_percentage, total_potential_savings
- avg_payback_period_months
- highest_roi_percentage, lowest_roi_percentage

---

## Example Calculations

### Example 1: Small Contractor

**Input:**
- Project Value: $300,000
- Delay Percentage: 50%
- Projects Per Year: 2
- Average Delay Days: 37

**Calculation:**
```
Annual Delayed Projects = (50 / 100) × 2 = 1 project
Annual Delay Cost = 1 × 37 × $45,662 = $1,689,494
Estimated Savings = ($1,689,494 × 0.65) - $5,000 = $1,093,171
Monthly Savings = $1,093,171 / 12 = $91,098
Payback Period = $5,000 / $91,098 = 0.05 months (1.5 days)
ROI % = ($1,093,171 / $5,000) × 100 = 21,863%
```

**Result:**
- Payback in 1.5 days
- ROI: 21,863%
- Annual Savings: $1,093,171

---

### Example 2: Large Contractor

**Input:**
- Project Value: $2,000,000
- Delay Percentage: 80%
- Projects Per Year: 10
- Average Delay Days: 37

**Calculation:**
```
Annual Delayed Projects = (80 / 100) × 10 = 8 projects
Annual Delay Cost = 8 × 37 × $45,662 = $13,515,952
Estimated Savings = ($13,515,952 × 0.65) - $5,000 = $8,785,369
Monthly Savings = $8,785,369 / 12 = $732,114
Payback Period = $5,000 / $732,114 = 0.007 months (2 hours)
ROI % = ($8,785,369 / $5,000) × 100 = 175,707%
```

**Result:**
- Payback in 2 hours
- ROI: 175,707%
- Annual Savings: $8,785,369

---

## Error Handling

### Validation Errors (422)
```json
{
    "detail": [
        {
            "loc": ["body", "delay_percentage"],
            "msg": "ensure this value is less than or equal to 100",
            "type": "value_error.number.not_le"
        }
    ]
}
```

### Contractor Not Found (404)
```json
{
    "detail": "Contractor with email 'john@abcconstruction.com' not found"
}
```

### Invalid Calculation Parameters (400)
```json
{
    "detail": "Invalid calculation parameters: Project value must be greater than 0"
}
```

### Calculation Not Found (404)
```json
{
    "detail": "ROI calculation with id 999 not found"
}
```

### Database Error (500)
```json
{
    "detail": "Failed to calculate ROI"
}
```

---

## Integration with main.py

```python
from app.routes import roi

app.include_router(roi.router, tags=["roi"])
```

---

## Testing Workflow

### 1. Calculate ROI
```bash
curl -X POST http://localhost:8000/api/roi/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@abcconstruction.com",
    "project_value": 500000,
    "delay_percentage": 75,
    "projects_per_year": 4
  }'
```

### 2. Get ROI Summary
```bash
curl http://localhost:8000/api/roi/roi-summary/john@abcconstruction.com
```

### 3. List Calculations
```bash
curl http://localhost:8000/api/roi/calculations
```

### 4. Get Statistics
```bash
curl http://localhost:8000/api/roi/stats
```

---

## Database Queries

### Get all calculations for a contractor
```python
calculations = db.query(ROICalculation).filter(
    ROICalculation.contractor_id == contractor_id
).all()
```

### Get latest calculation for a contractor
```python
latest = db.query(ROICalculation).filter(
    ROICalculation.contractor_id == contractor_id
).order_by(
    ROICalculation.calculation_date.desc()
).first()
```

### Get high-ROI contractors
```python
high_roi = db.query(Contractor).filter(
    Contractor.roi_percentage > 1000
).all()
```

### Get ROI statistics
```python
total = db.query(func.count(ROICalculation.id)).scalar()
avg_savings = db.query(func.avg(ROICalculation.estimated_annual_savings)).scalar()
avg_roi = db.query(func.avg(ROICalculation.roi_percentage)).scalar()
```

---

## File Placement

```
app/
├── routes/
│   ├── __init__.py
│   ├── forms.py
│   ├── roi.py                 # ← This file
│   ├── booking.py
│   └── contractor.py
├── models/
│   └── contractor.py
├── schemas/
│   └── contractor.py
├── config.py
├── database.py
└── main.py
```

---

## Summary

The `app/routes/roi.py` module provides:

✅ **ROI calculations** - Industry-standard formulas
✅ **Financial analysis** - Comprehensive metrics
✅ **Database integration** - Save calculations
✅ **Contractor updates** - Update with ROI data
✅ **Email automation** - Send ROI reports
✅ **Statistics** - Aggregated data
✅ **Filtering & pagination** - List calculations
✅ **Error handling** - Detailed error responses
✅ **Logging** - Detailed operation logging
✅ **Validation** - Comprehensive input validation

Everything is production-ready and fully documented!
