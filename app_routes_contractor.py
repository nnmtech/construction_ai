"""
Construction AI Landing Page - Contractor Routes

This module defines all CRUD endpoints for the Contractor model:
- POST /api/contractors - Create contractor
- GET /api/contractors - List contractors with pagination and filtering
- GET /api/contractors/{contractor_id} - Get single contractor
- PUT /api/contractors/{contractor_id} - Update contractor
- DELETE /api/contractors/{contractor_id} - Delete contractor
- GET /api/contractors/stats - Get contractor statistics
- GET /api/contractors/by-email/{email} - Get contractor by email
- GET /api/contractors/by-status/{status} - Get contractors by status

Features:
- Full CRUD operations
- Pagination and filtering
- Search by email and status
- Statistics endpoint
- Comprehensive error handling
- Request/response validation with Pydantic
- Database dependency injection

Usage:
    from app.routes.contractor import router
    app.include_router(router)
"""

import logging
from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.database import get_db
from app.models.contractor import Contractor
from app.schemas.contractor import (
    ContractorCreate,
    ContractorUpdate,
    ContractorResponse,
    ContractorListResponse,
    ContractorStatistics,
    ErrorResponse
)

# ============================================================================
# ROUTER CONFIGURATION
# ============================================================================

router = APIRouter(
    prefix="/api/contractors",
    tags=["contractors"],
    responses={
        404: {"model": ErrorResponse, "description": "Contractor not found"},
        400: {"model": ErrorResponse, "description": "Bad request"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

logger = logging.getLogger(__name__)

# ============================================================================
# CREATE ENDPOINT
# ============================================================================

@router.post(
    "",
    response_model=ContractorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new contractor",
    description="Create a new contractor record with company and contact information"
)
async def create_contractor(
    contractor_data: ContractorCreate,
    db: Session = Depends(get_db)
) -> ContractorResponse:
    """
    Create a new contractor.
    
    **Request Body:**
    - company_name: Name of the construction company (required)
    - contact_name: Name of primary contact person (required)
    - email: Email address (required, must be unique)
    - phone: Phone number (optional)
    - company_size: small, medium, or large (optional)
    - annual_revenue: Annual revenue in dollars (optional)
    - current_challenges: Description of challenges (optional)
    - industry_focus: commercial, residential, or mixed (optional)
    
    **Returns:**
    - ContractorResponse: Created contractor with ID and timestamps
    
    **Raises:**
    - 400: Email already exists
    - 422: Validation error
    - 500: Database error
    
    **Example:**
    ```
    POST /api/contractors
    {
        "company_name": "ABC Construction",
        "contact_name": "John Smith",
        "email": "john@abcconstruction.com",
        "phone": "404-555-0123",
        "company_size": "medium",
        "annual_revenue": 5000000,
        "current_challenges": "Schedule delays and subcontractor coordination"
    }
    ```
    """
    
    try:
        # Check if email already exists
        existing = db.query(Contractor).filter(
            Contractor.email == contractor_data.email
        ).first()
        
        if existing:
            logger.warning(f"Attempt to create contractor with existing email: {contractor_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Contractor with email '{contractor_data.email}' already exists"
            )
        
        # Create new contractor
        db_contractor = Contractor(**contractor_data.dict())
        db.add(db_contractor)
        db.commit()
        db.refresh(db_contractor)
        
        logger.info(f"✓ Created contractor: {db_contractor.id} ({db_contractor.company_name})")
        
        return ContractorResponse.from_orm(db_contractor)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"✗ Error creating contractor: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create contractor"
        )


# ============================================================================
# LIST ENDPOINT
# ============================================================================

@router.get(
    "",
    response_model=ContractorListResponse,
    summary="List all contractors",
    description="Get a paginated list of contractors with optional filtering"
)
async def list_contractors(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    company_size: Optional[str] = Query(None, description="Filter by company size"),
    conversion_status: Optional[str] = Query(None, description="Filter by conversion status"),
    demo_scheduled: Optional[bool] = Query(None, description="Filter by demo scheduled"),
    search: Optional[str] = Query(None, description="Search by company name or email"),
    db: Session = Depends(get_db)
) -> ContractorListResponse:
    """
    List contractors with pagination and filtering.
    
    **Query Parameters:**
    - page: Page number (default: 1)
    - page_size: Items per page (default: 10, max: 100)
    - company_size: Filter by size (small, medium, large)
    - conversion_status: Filter by status (lead, prospect, customer, lost)
    - demo_scheduled: Filter by demo scheduled (true/false)
    - search: Search by company name or email
    
    **Returns:**
    - ContractorListResponse: Paginated list of contractors
    
    **Example:**
    ```
    GET /api/contractors?page=1&page_size=10&company_size=medium&conversion_status=prospect
    ```
    """
    
    try:
        # Build query
        query = db.query(Contractor)
        
        # Apply filters
        if company_size:
            query = query.filter(Contractor.company_size == company_size)
        
        if conversion_status:
            query = query.filter(Contractor.conversion_status == conversion_status)
        
        if demo_scheduled is not None:
            query = query.filter(Contractor.demo_scheduled == demo_scheduled)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Contractor.company_name.ilike(search_term)) |
                (Contractor.email.ilike(search_term))
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        skip = (page - 1) * page_size
        contractors = query.order_by(
            Contractor.created_at.desc()
        ).offset(skip).limit(page_size).all()
        
        logger.info(f"✓ Listed contractors: page={page}, size={page_size}, total={total}")
        
        return ContractorListResponse(
            total=total,
            count=len(contractors),
            page=page,
            page_size=page_size,
            contractors=[ContractorResponse.from_orm(c) for c in contractors]
        )
        
    except Exception as e:
        logger.error(f"✗ Error listing contractors: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list contractors"
        )


# ============================================================================
# GET SINGLE ENDPOINT
# ============================================================================

@router.get(
    "/{contractor_id}",
    response_model=ContractorResponse,
    summary="Get contractor by ID",
    description="Get a specific contractor by their ID"
)
async def get_contractor(
    contractor_id: int = Path(..., ge=1, description="Contractor ID"),
    db: Session = Depends(get_db)
) -> ContractorResponse:
    """
    Get a single contractor by ID.
    
    **Path Parameters:**
    - contractor_id: Unique contractor identifier
    
    **Returns:**
    - ContractorResponse: Contractor details
    
    **Raises:**
    - 404: Contractor not found
    - 500: Database error
    
    **Example:**
    ```
    GET /api/contractors/1
    ```
    """
    
    try:
        contractor = db.query(Contractor).filter(
            Contractor.id == contractor_id
        ).first()
        
        if not contractor:
            logger.warning(f"Contractor not found: {contractor_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Contractor with id {contractor_id} not found"
            )
        
        logger.info(f"✓ Retrieved contractor: {contractor_id}")
        
        return ContractorResponse.from_orm(contractor)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"✗ Error retrieving contractor: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve contractor"
        )


# ============================================================================
# GET BY EMAIL ENDPOINT
# ============================================================================

@router.get(
    "/by-email/{email}",
    response_model=ContractorResponse,
    summary="Get contractor by email",
    description="Get a contractor by their email address"
)
async def get_contractor_by_email(
    email: str = Path(..., description="Contractor email address"),
    db: Session = Depends(get_db)
) -> ContractorResponse:
    """
    Get a contractor by email address.
    
    **Path Parameters:**
    - email: Contractor email address
    
    **Returns:**
    - ContractorResponse: Contractor details
    
    **Raises:**
    - 404: Contractor not found
    - 500: Database error
    
    **Example:**
    ```
    GET /api/contractors/by-email/john@abcconstruction.com
    ```
    """
    
    try:
        contractor = db.query(Contractor).filter(
            Contractor.email == email
        ).first()
        
        if not contractor:
            logger.warning(f"Contractor not found by email: {email}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Contractor with email '{email}' not found"
            )
        
        logger.info(f"✓ Retrieved contractor by email: {email}")
        
        return ContractorResponse.from_orm(contractor)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"✗ Error retrieving contractor by email: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve contractor"
        )


# ============================================================================
# GET BY STATUS ENDPOINT
# ============================================================================

@router.get(
    "/by-status/{status}",
    response_model=ContractorListResponse,
    summary="Get contractors by conversion status",
    description="Get all contractors with a specific conversion status"
)
async def get_contractors_by_status(
    status: str = Path(..., description="Conversion status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
) -> ContractorListResponse:
    """
    Get contractors by conversion status.
    
    **Path Parameters:**
    - status: Conversion status (lead, prospect, customer, lost)
    
    **Query Parameters:**
    - page: Page number (default: 1)
    - page_size: Items per page (default: 10)
    
    **Returns:**
    - ContractorListResponse: Paginated list of contractors
    
    **Example:**
    ```
    GET /api/contractors/by-status/prospect?page=1&page_size=10
    ```
    """
    
    try:
        # Validate status
        valid_statuses = ['lead', 'prospect', 'customer', 'lost']
        if status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
        
        # Query contractors
        query = db.query(Contractor).filter(
            Contractor.conversion_status == status
        )
        
        total = query.count()
        skip = (page - 1) * page_size
        contractors = query.order_by(
            Contractor.created_at.desc()
        ).offset(skip).limit(page_size).all()
        
        logger.info(f"✓ Listed contractors by status: {status}, page={page}")
        
        return ContractorListResponse(
            total=total,
            count=len(contractors),
            page=page,
            page_size=page_size,
            contractors=[ContractorResponse.from_orm(c) for c in contractors]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"✗ Error retrieving contractors by status: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve contractors"
        )


# ============================================================================
# UPDATE ENDPOINT
# ============================================================================

@router.put(
    "/{contractor_id}",
    response_model=ContractorResponse,
    summary="Update contractor",
    description="Update a contractor's information"
)
async def update_contractor(
    contractor_id: int = Path(..., ge=1, description="Contractor ID"),
    contractor_data: ContractorUpdate = None,
    db: Session = Depends(get_db)
) -> ContractorResponse:
    """
    Update a contractor.
    
    **Path Parameters:**
    - contractor_id: Unique contractor identifier
    
    **Request Body:**
    - All fields are optional - only provided fields will be updated
    
    **Returns:**
    - ContractorResponse: Updated contractor
    
    **Raises:**
    - 404: Contractor not found
    - 400: Email already exists
    - 422: Validation error
    - 500: Database error
    
    **Example:**
    ```
    PUT /api/contractors/1
    {
        "conversion_status": "prospect",
        "demo_scheduled": true,
        "estimated_annual_savings": 1000000
    }
    ```
    """
    
    try:
        # Get contractor
        contractor = db.query(Contractor).filter(
            Contractor.id == contractor_id
        ).first()
        
        if not contractor:
            logger.warning(f"Contractor not found for update: {contractor_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Contractor with id {contractor_id} not found"
            )
        
        # Check if email is being updated to an existing email
        if contractor_data.email and contractor_data.email != contractor.email:
            existing = db.query(Contractor).filter(
                Contractor.email == contractor_data.email
            ).first()
            
            if existing:
                logger.warning(f"Attempt to update contractor to existing email: {contractor_data.email}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Contractor with email '{contractor_data.email}' already exists"
                )
        
        # Update fields
        update_data = contractor_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(contractor, key, value)
        
        db.commit()
        db.refresh(contractor)
        
        logger.info(f"✓ Updated contractor: {contractor_id}")
        
        return ContractorResponse.from_orm(contractor)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"✗ Error updating contractor: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update contractor"
        )


# ============================================================================
# DELETE ENDPOINT
# ============================================================================

@router.delete(
    "/{contractor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete contractor",
    description="Delete a contractor and all related records"
)
async def delete_contractor(
    contractor_id: int = Path(..., ge=1, description="Contractor ID"),
    db: Session = Depends(get_db)
) -> None:
    """
    Delete a contractor.
    
    **Path Parameters:**
    - contractor_id: Unique contractor identifier
    
    **Note:** This will also delete all related contact submissions, ROI calculations, and demo bookings.
    
    **Raises:**
    - 404: Contractor not found
    - 500: Database error
    
    **Example:**
    ```
    DELETE /api/contractors/1
    ```
    """
    
    try:
        # Get contractor
        contractor = db.query(Contractor).filter(
            Contractor.id == contractor_id
        ).first()
        
        if not contractor:
            logger.warning(f"Contractor not found for deletion: {contractor_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Contractor with id {contractor_id} not found"
            )
        
        # Delete contractor (cascade will delete related records)
        db.delete(contractor)
        db.commit()
        
        logger.info(f"✓ Deleted contractor: {contractor_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"✗ Error deleting contractor: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete contractor"
        )


# ============================================================================
# STATISTICS ENDPOINT
# ============================================================================

@router.get(
    "/stats/overview",
    response_model=ContractorStatistics,
    summary="Get contractor statistics",
    description="Get overview statistics about all contractors"
)
async def get_contractor_statistics(
    status: str = Path(..., description="Conversion status"),
) -> ContractorStatistics:
    """
    Get contractor statistics.
    
    **Returns:**
    - ContractorStatistics: Overview statistics
    
    **Includes:**
    - Total contractors
    - Breakdown by conversion status
    - Demo statistics
    - Average savings and ROI
    - Total potential savings
    
    **Example:**
    ```
    GET /api/contractors/stats/overview
    ```
    """
    
    try:
        # Get total count
        total = db.query(func.count(Contractor.id)).scalar()
        
        # Get counts by status
        leads = db.query(func.count(Contractor.id)).filter(
            Contractor.conversion_status == 'lead'
        ).scalar()
        
        prospects = db.query(func.count(Contractor.id)).filter(
            Contractor.conversion_status == 'prospect'
        ).scalar()
        
        customers = db.query(func.count(Contractor.id)).filter(
            Contractor.conversion_status == 'customer'
        ).scalar()
        
        lost = db.query(func.count(Contractor.id)).filter(
            Contractor.conversion_status == 'lost'
        ).scalar()
        
        # Get demo statistics
        demos_scheduled = db.query(func.count(Contractor.id)).filter(
            Contractor.demo_scheduled == True
        ).scalar()
        
        demos_completed = db.query(func.count(Contractor.id)).filter(
            Contractor.demo_completed == True
        ).scalar()
        
        # Get average savings and ROI
        avg_savings = db.query(
            func.avg(Contractor.estimated_annual_savings)
        ).filter(
            Contractor.estimated_annual_savings.isnot(None)
        ).scalar()
        
        avg_roi = db.query(
            func.avg(Contractor.roi_percentage)
        ).filter(
            Contractor.roi_percentage.isnot(None)
        ).scalar()
        
        # Get total potential savings
        total_savings = db.query(
            func.sum(Contractor.estimated_annual_savings)
        ).filter(
            Contractor.estimated_annual_savings.isnot(None)
        ).scalar()
        
        logger.info(f"✓ Retrieved contractor statistics")
        
        return ContractorStatistics(
            total_contractors=total or 0,
            leads=leads or 0,
            prospects=prospects or 0,
            customers=customers or 0,
            lost=lost or 0,
            demos_scheduled=demos_scheduled or 0,
            demos_completed=demos_completed or 0,
            avg_estimated_savings=avg_savings,
            avg_roi_percentage=avg_roi,
            total_potential_savings=total_savings
        )
        
    except Exception as e:
        logger.error(f"✗ Error retrieving statistics: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve statistics"
        )


# ============================================================================
# ROUTER INITIALIZATION LOGGING
# ============================================================================

logger.info("Contractor routes loaded:")
logger.info("✓ POST /api/contractors - Create contractor")
logger.info("✓ GET /api/contractors - List contractors")
logger.info("✓ GET /api/contractors/{id} - Get contractor")
logger.info("✓ GET /api/contractors/by-email/{email} - Get by email")
logger.info("✓ GET /api/contractors/by-status/{status} - Get by status")
logger.info("✓ PUT /api/contractors/{id} - Update contractor")
logger.info("✓ DELETE /api/contractors/{id} - Delete contractor")
logger.info("✓ GET /api/contractors/stats/overview - Get statistics")
