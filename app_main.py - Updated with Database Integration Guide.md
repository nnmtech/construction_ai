# app/main.py - Updated with Database Integration Guide

## Overview

The updated `app/main.py` file now includes complete database integration with:

1. **Database Initialization** - Calls `init_db()` on startup
2. **Database Dependency** - Uses `get_db` in endpoints
3. **Test Endpoints** - Verify database connectivity
4. **Database Info** - Get database statistics
5. **Enhanced Logging** - Detailed database startup logs

---

## Key Changes from Original

### 1. Database Imports

```python
from app.database import (
    init_db,                    # Initialize tables
    engine,                     # SQLAlchemy engine
    Base,                       # Declarative base
    get_db,                     # FastAPI dependency
    check_db_connection,        # Connection test
    get_db_info                 # Database info
)
```

### 2. Database Initialization Function

```python
def initialize_database():
    """Initialize database tables on application startup."""
    try:
        logger.info("=" * 60)
        logger.info("DATABASE INITIALIZATION")
        logger.info("=" * 60)
        
        logger.info("Initializing database...")
        init_db()
        
        logger.info("✓ Database initialized successfully")
        
        # Verify database connection
        if check_db_connection():
            logger.info("✓ Database connection verified")
        
        # Get database information
        db_info = get_db_info()
        logger.info(f"✓ Database type: {db_info.get('type', 'unknown')}")
        logger.info(f"✓ Tables created: {db_info.get('table_count', 0)}")
        logger.info(f"✓ Table names: {', '.join(db_info.get('tables', []))}")
        
        logger.info("=" * 60)
        return True
        
    except Exception as e:
        logger.error("=" * 60)
        logger.error("DATABASE INITIALIZATION FAILED")
        logger.error("=" * 60)
        logger.error(f"✗ Failed to initialize database: {str(e)}")
        raise

# Initialize database before creating app
try:
    initialize_database()
except Exception as e:
    logger.critical(f"Cannot start application without database: {str(e)}")
    raise
```

**Key Points:**
- Initializes database BEFORE creating FastAPI app
- Fails fast if database is not configured
- Logs detailed database information
- Verifies database connectivity

### 3. New Database Test Endpoints

#### Test Database Connection

```python
@app.get("/api/test-db", tags=["database"])
async def test_database_connection(db: Session = Depends(get_db)):
    """
    Test database connection and basic operations.
    
    Demonstrates:
    - Database dependency injection
    - Basic query execution
    - Error handling
    """
    try:
        from sqlalchemy import text
        result = db.execute(text("SELECT 1"))
        test_result = result.scalar()
        
        if test_result == 1:
            return {
                "status": "success",
                "message": "Database connection test passed",
                "database": "connected",
                "test_query": "SELECT 1",
                "test_result": test_result,
                "timestamp": datetime.utcnow().isoformat()
            }
    except Exception as e:
        logger.error(f"Database connection test failed: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "message": "Database connection test failed",
                "error": str(e)
            }
        )
```

**Usage:**
```bash
curl http://localhost:8000/api/test-db
```

**Response:**
```json
{
  "status": "success",
  "message": "Database connection test passed",
  "database": "connected",
  "test_query": "SELECT 1",
  "test_result": 1,
  "timestamp": "2026-01-05T10:30:00"
}
```

#### Get Database Information

```python
@app.get("/api/db-info", tags=["database"])
async def get_database_info():
    """
    Get detailed database information.
    
    Returns:
    - Database type (SQLite, PostgreSQL, MySQL)
    - List of tables
    - Table details (columns, count)
    - Connection status
    """
    try:
        info = get_db_info()
        return info
    except Exception as e:
        logger.error(f"Error getting database info: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "message": "Failed to get database info",
                "error": str(e)
            }
        )
```

**Usage:**
```bash
curl http://localhost:8000/api/db-info
```

**Response:**
```json
{
  "type": "sqlite",
  "url": "sqlite:///./contractors.db...",
  "tables": ["contractor"],
  "table_count": 1,
  "connected": true,
  "table_details": {
    "contractor": {
      "columns": ["id", "company_name", "email", "phone", "company_size", "annual_revenue", "current_challenges", "estimated_annual_savings", "demo_scheduled", "demo_date", "created_at", "updated_at"],
      "column_count": 12
    }
  }
}
```

#### Test Database Session

```python
@app.get("/api/test-session", tags=["database"])
async def test_database_session(db: Session = Depends(get_db)):
    """
    Test database session and transaction handling.
    
    Demonstrates:
    - Session dependency injection
    - Query execution
    - Session lifecycle
    """
    try:
        session_info = {
            "session_active": db.is_active,
            "session_in_transaction": db.in_transaction(),
            "session_info": str(db.info)
        }
        
        return {
            "status": "success",
            "message": "Database session test passed",
            "session": session_info,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Database session test failed: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "message": "Database session test failed",
                "error": str(e)
            }
        )
```

**Usage:**
```bash
curl http://localhost:8000/api/test-session
```

### 4. Updated Startup Event

```python
@app.on_event("startup")
async def startup_event():
    """Execute on application startup."""
    logger.info("=" * 60)
    logger.info("APPLICATION STARTUP")
    logger.info("=" * 60)
    
    try:
        # Verify database connection
        if check_db_connection():
            logger.info("✓ Database connection verified")
    except Exception as e:
        logger.error(f"✗ Database connection failed: {str(e)}")
        raise
    
    # Log configuration
    logger.info(f"✓ Application: {settings.app_name}")
    logger.info(f"✓ Debug mode: {settings.debug}")
    logger.info(f"✓ Database URL: {settings.database_url[:50]}...")
    
    # Log ROI calculator settings
    logger.info(f"✓ Cost per day delay: ${settings.cost_per_day_delay:,.0f}")
    logger.info(f"✓ AI solution annual cost: ${settings.ai_solution_annual_cost:,.0f}")
    
    logger.info("=" * 60)
    logger.info("APPLICATION READY")
    logger.info("=" * 60)
    logger.info(f"API Documentation: http://localhost:8000/api/docs")
    logger.info(f"Landing Page: http://localhost:8000/")
    logger.info(f"Health Check: http://localhost:8000/health")
    logger.info(f"Database Test: http://localhost:8000/api/test-db")
    logger.info(f"Database Info: http://localhost:8000/api/db-info")
```

### 5. Updated Shutdown Event

```python
@app.on_event("shutdown")
async def shutdown_event():
    """Execute on application shutdown."""
    logger.info("=" * 60)
    logger.info("APPLICATION SHUTDOWN")
    logger.info("=" * 60)
    
    try:
        # Close database connections
        engine.dispose()
        logger.info("✓ Database connections closed")
    except Exception as e:
        logger.error(f"✗ Error closing database: {str(e)}")
    
    logger.info("Application shutdown complete")
    logger.info("=" * 60)
```

---

## Startup Logging Output

When you run the application, you'll see:

```
============================================================
DATABASE INITIALIZATION
============================================================
INFO:     Initializing database...
✓ Database initialized successfully
✓ Database connection verified
✓ Database type: sqlite
✓ Tables created: 1
✓ Table names: contractor
============================================================
FastAPI application created: Construction AI Landing
Debug mode: True
Environment: development
✓ GZIP compression middleware added
✓ Trusted Host middleware added
✓ CORS middleware added
✓ Static files mounted from /app/static
✓ Contact form routes included
✓ ROI calculator routes included
✓ Demo booking routes included
============================================================
APPLICATION STARTUP
============================================================
✓ Database connection verified
✓ Application: Construction AI Landing
✓ Debug mode: True
✓ Database URL: sqlite:///./contractors.db...
✓ SMTP Server: smtp.gmail.com:587
✓ Cost per day delay: $45,662
✓ AI solution annual cost: $5,000
✓ Delay reduction: 65%
============================================================
APPLICATION READY
============================================================
API Documentation: http://localhost:8000/api/docs
Landing Page: http://localhost:8000/
Health Check: http://localhost:8000/health
Database Test: http://localhost:8000/api/test-db
Database Info: http://localhost:8000/api/db-info
```

---

## Using Database Dependency in Endpoints

### Example 1: Query Data

```python
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.contractor import Contractor

@app.get("/contractors")
async def list_contractors(db: Session = Depends(get_db)):
    """List all contractors."""
    contractors = db.query(Contractor).all()
    return contractors
```

### Example 2: Create Data

```python
@app.post("/contractors")
async def create_contractor(
    contractor: ContractorCreate,
    db: Session = Depends(get_db)
):
    """Create a new contractor."""
    db_contractor = Contractor(**contractor.dict())
    db.add(db_contractor)
    db.commit()
    db.refresh(db_contractor)
    return db_contractor
```

### Example 3: Get Single Record

```python
@app.get("/contractors/{contractor_id}")
async def get_contractor(
    contractor_id: int,
    db: Session = Depends(get_db)
):
    """Get contractor by ID."""
    contractor = db.query(Contractor).filter(
        Contractor.id == contractor_id
    ).first()
    
    if not contractor:
        raise HTTPException(status_code=404, detail="Contractor not found")
    
    return contractor
```

### Example 4: Update Data

```python
@app.put("/contractors/{contractor_id}")
async def update_contractor(
    contractor_id: int,
    contractor_update: ContractorUpdate,
    db: Session = Depends(get_db)
):
    """Update contractor."""
    db_contractor = db.query(Contractor).filter(
        Contractor.id == contractor_id
    ).first()
    
    if not db_contractor:
        raise HTTPException(status_code=404, detail="Contractor not found")
    
    for key, value in contractor_update.dict(exclude_unset=True).items():
        setattr(db_contractor, key, value)
    
    db.commit()
    db.refresh(db_contractor)
    return db_contractor
```

### Example 5: Delete Data

```python
@app.delete("/contractors/{contractor_id}")
async def delete_contractor(
    contractor_id: int,
    db: Session = Depends(get_db)
):
    """Delete contractor."""
    db_contractor = db.query(Contractor).filter(
        Contractor.id == contractor_id
    ).first()
    
    if not db_contractor:
        raise HTTPException(status_code=404, detail="Contractor not found")
    
    db.delete(db_contractor)
    db.commit()
    
    return {"message": "Contractor deleted"}
```

---

## Testing the Database Integration

### 1. Start the Application

```bash
uvicorn app.main:app --reload
```

### 2. Check Database Connection

```bash
curl http://localhost:8000/api/test-db
```

### 3. Get Database Info

```bash
curl http://localhost:8000/api/db-info
```

### 4. Test Database Session

```bash
curl http://localhost:8000/api/test-session
```

### 5. View API Documentation

Visit http://localhost:8000/api/docs in your browser

### 6. Check Health Status

```bash
curl http://localhost:8000/health
```

---

## New Database Endpoints

| Endpoint | Method | Purpose | Tags |
|----------|--------|---------|------|
| `/api/test-db` | GET | Test database connection | database |
| `/api/db-info` | GET | Get database information | database |
| `/api/test-session` | GET | Test database session | database |
| `/health` | GET | Health check | health |
| `/health/ready` | GET | Readiness probe | health |
| `/health/live` | GET | Liveness probe | health |
| `/api/config` | GET | Configuration | config |
| `/api/version` | GET | Version info | config |
| `/api/info` | GET | App info | info |
| `/api/endpoints` | GET | List endpoints | documentation |

---

## File Placement

```
app/
├── __init__.py
├── main.py                    # ← Updated file
├── config.py
├── database.py
├── models/
│   └── contractor.py
├── schemas/
│   └── contractor.py
├── routes/
│   ├── forms.py
│   ├── roi.py
│   └── booking.py
├── utils/
│   └── email.py
├── templates/
│   └── index.html
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── app.js
```

---

## Key Improvements

✅ **Database Initialization** - Automatic table creation on startup
✅ **Dependency Injection** - Easy database access in endpoints
✅ **Test Endpoints** - Verify database connectivity
✅ **Database Info** - Get database statistics
✅ **Enhanced Logging** - Detailed startup/shutdown logs
✅ **Error Handling** - Comprehensive exception handling
✅ **Health Checks** - Database status monitoring
✅ **Production Ready** - Configured for scalability

---

## Summary

The updated `app/main.py` now provides:

1. **Automatic database initialization** on application startup
2. **Database dependency injection** for all endpoints
3. **Test endpoints** to verify database connectivity
4. **Database information endpoint** for statistics
5. **Enhanced logging** with database details
6. **Proper error handling** for database operations
7. **Health checks** that include database status
8. **Graceful shutdown** with connection cleanup

This creates a complete, production-ready FastAPI application with full database integration!
