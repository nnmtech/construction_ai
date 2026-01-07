"""
Construction AI Landing Page - ROI Calculator Routes

This module defines endpoints for ROI calculations:
- POST /api/roi/calculate - Calculate ROI based on project data
- GET /api/roi/roi-summary/{email} - Get previously calculated ROI
- GET /api/roi/calculations - List all calculations (admin)
- GET /api/roi/calculations/{id} - Get calculation details
- GET /api/roi/stats - Get ROI statistics

Features:
- ROI calculation based on industry-standard formulas
- Saves calculations to database
- Updates contractor with ROI data
- Sends ROI report email
- Comprehensive financial analysis
- Detailed breakdowns and metrics
- Error handling and validation
- Database integration with SQLAlchemy

ROI Calculation Formula:
- Annual Delay Costs = Days Delayed × Projects/Year × Cost Per Day
- Estimated Savings = Annual Delay Costs × Delay Reduction % - AI Solution Cost
- Payback Period = AI Solution Cost / Monthly Savings
- ROI % = (Estimated Savings / AI Solution Cost) × 100

Usage:
    from app.routes.roi import router
    app.include_router(router)
"""

import logging
import math
from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Path, BackgroundTasks, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.contractor import Contractor, ROICalculation
from app.config import settings
from app.utils.email import send_roi_report_email

# ============================================================================
# ROUTER CONFIGURATION
# ============================================================================

router = APIRouter(
    prefix="/api/roi",
    tags=["roi"],
    responses={
        404: {"description": "Not found"},
        400: {"description": "Bad request"},
        500: {"description": "Internal server error"}
    }
)

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

logger = logging.getLogger(__name__)

# ============================================================================
# SCHEMAS FOR ROI ROUTES
# ============================================================================

from pydantic import BaseModel, EmailStr, Field

class ROICalculationRequest(BaseModel):
    """Schema for ROI calculation request."""
    
    email: EmailStr = Field(
        ...,
        description="Contractor email address"
    )
    
    project_value: float = Field(
        ...,
        gt=0,
        description="Average project value in dollars"
    )
    
    delay_percentage: float = Field(
        ...,
        ge=0,
        le=100,
        description="Percentage of projects that experience delays (0-100)"
    )
    
    projects_per_year: int = Field(
        ...,
        gt=0,
        description="Number of projects per year"
    )
    
    avg_delay_days: Optional[float] = Field(
        None,
        ge=0,
        description="Average delay in days (optional, defaults to 37)"
    )
    
    company_size: Optional[str] = Field(
        None,
        description="Company size: small, medium, large"
    )
    
    industry_focus: Optional[str] = Field(
        None,
        description="Industry focus: commercial, residential, mixed"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "john@abcconstruction.com",
                "project_value": 500000,
                "delay_percentage": 75,
                "projects_per_year": 4,
                "avg_delay_days": 37,
                "company_size": "medium",
                "industry_focus": "commercial"
            }
        }


class FinancialMetrics(BaseModel):
    """Schema for financial metrics."""
    
    annual_delay_cost: float = Field(
        ...,
        description="Total annual cost of delays in dollars"
    )
    
    annual_delayed_projects: float = Field(
        ...,
        description="Number of delayed projects per year"
    )
    
    estimated_annual_savings: float = Field(
        ...,
        description="Estimated annual savings with AI solution"
    )
    
    monthly_savings: float = Field(
        ...,
        description="Estimated monthly savings"
    )
    
    ai_solution_annual_cost: float = Field(
        ...,
        description="Annual cost of AI solution"
    )
    
    net_annual_benefit: float = Field(
        ...,
        description="Net annual benefit (savings - cost)"
    )
    
    payback_period_months: float = Field(
        ...,
        description="Payback period in months"
    )
    
    roi_percentage: float = Field(
        ...,
        description="Return on investment percentage"
    )
    
    break_even_months: float = Field(
        ...,
        description="Break-even point in months"
    )


class ROICalculationResponse(BaseModel):
    """Schema for ROI calculation response."""
    
    id: int
    contractor_id: int
    email: str
    project_value: float
    delay_percentage: float
    projects_per_year: int
    avg_delay_days: float
    financial_metrics: FinancialMetrics
    calculation_date: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class ROISummaryResponse(BaseModel):
    """Schema for ROI summary response."""
    
    contractor_id: int
    email: str
    company_name: str
    estimated_annual_savings: float
    roi_percentage: float
    payback_period_months: float
    last_calculation_date: datetime
    calculation_count: int


class ROICalculationListResponse(BaseModel):
    """Schema for ROI calculation list response."""
    
    total: int
    count: int
    page: int
    page_size: int
    calculations: List[ROICalculationResponse]


class ROIStatsResponse(BaseModel):
    """Schema for ROI statistics."""
    
    total_calculations: int
    avg_estimated_savings: float
    avg_roi_percentage: float
    total_potential_savings: float
    contractors_with_roi: int
    avg_payback_period_months: float
    highest_roi_percentage: float
    lowest_roi_percentage: float


# ============================================================================
# ROI CALCULATION LOGIC
# ============================================================================

class ROICalculator:
    """
    ROI Calculator for construction companies.
    
    Calculates return on investment for AI project management solutions
    based on industry-standard formulas and construction metrics.
    """
    
    def __init__(self, settings):
        """
        Initialize ROI calculator with settings.
        
        Args:
            settings: Application settings with ROI constants
        """
        self.cost_per_day_delay = settings.cost_per_day_delay
        self.ai_solution_annual_cost = settings.ai_solution_annual_cost
        self.delay_reduction_percentage = settings.delay_reduction_percentage
        self.avg_project_duration_days = settings.avg_project_duration_days
    
    def calculate(
        self,
        project_value: float,
        delay_percentage: float,
        projects_per_year: int,
        avg_delay_days: Optional[float] = None
    ) -> dict:
        """
        Calculate ROI metrics.
        
        Args:
            project_value: Average project value in dollars
            delay_percentage: Percentage of projects with delays (0-100)
            projects_per_year: Number of projects per year
            avg_delay_days: Average delay in days (optional)
            
        Returns:
            Dictionary with detailed financial metrics
            
        Raises:
            ValueError: If inputs are invalid
        """
        
        # Use default delay days if not provided
        if avg_delay_days is None:
            avg_delay_days = self.avg_project_duration_days
        
        # Validate inputs
        if project_value <= 0:
            raise ValueError("Project value must be greater than 0")
        if delay_percentage < 0 or delay_percentage > 100:
            raise ValueError("Delay percentage must be between 0 and 100")
        if projects_per_year <= 0:
            raise ValueError("Projects per year must be greater than 0")
        if avg_delay_days < 0:
            raise ValueError("Average delay days must be non-negative")
        
        logger.info(f"Calculating ROI: project_value={project_value}, delay_percentage={delay_percentage}%, projects_per_year={projects_per_year}")
        
        # Calculate annual delay costs
        # Formula: Days Delayed × Projects/Year × Cost Per Day
        annual_delayed_projects = (delay_percentage / 100) * projects_per_year
        annual_delay_cost = annual_delayed_projects * avg_delay_days * self.cost_per_day_delay
        
        logger.debug(f"Annual delayed projects: {annual_delayed_projects}")
        logger.debug(f"Annual delay cost: ${annual_delay_cost:,.2f}")
        
        # Calculate estimated savings
        # Formula: Annual Delay Costs × Delay Reduction % - AI Solution Cost
        estimated_annual_savings = (annual_delay_cost * self.delay_reduction_percentage) - self.ai_solution_annual_cost
        
        logger.debug(f"Estimated annual savings: ${estimated_annual_savings:,.2f}")
        
        # Calculate monthly savings
        monthly_savings = estimated_annual_savings / 12
        
        # Calculate payback period
        # Formula: AI Solution Cost / Monthly Savings
        if monthly_savings > 0:
            payback_period_months = self.ai_solution_annual_cost / monthly_savings
        else:
            payback_period_months = float('inf')
        
        logger.debug(f"Payback period: {payback_period_months:.2f} months")
        
        # Calculate ROI percentage
        # Formula: (Estimated Savings / AI Solution Cost) × 100
        if self.ai_solution_annual_cost > 0:
            roi_percentage = (estimated_annual_savings / self.ai_solution_annual_cost) * 100
        else:
            roi_percentage = 0
        
        logger.debug(f"ROI percentage: {roi_percentage:.2f}%")
        
        # Calculate break-even point
        if monthly_savings > 0:
            break_even_months = self.ai_solution_annual_cost / monthly_savings
        else:
            break_even_months = float('inf')
        
        # Calculate net annual benefit
        net_annual_benefit = estimated_annual_savings
        
        return {
            "annual_delay_cost": round(annual_delay_cost, 2),
            "annual_delayed_projects": round(annual_delayed_projects, 2),
            "estimated_annual_savings": round(estimated_annual_savings, 2),
            "monthly_savings": round(monthly_savings, 2),
            "ai_solution_annual_cost": self.ai_solution_annual_cost,
            "net_annual_benefit": round(net_annual_benefit, 2),
            "payback_period_months": round(payback_period_months, 2) if payback_period_months != float('inf') else None,
            "roi_percentage": round(roi_percentage, 2),
            "break_even_months": round(break_even_months, 2) if break_even_months != float('inf') else None
        }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def send_roi_report_email_async(
    email: str,
    company_name: str,
    contact_name: str,
    roi_data: dict
):
    """
    Send ROI report email asynchronously.
    
    Args:
        email: Recipient email address
        company_name: Company name
        contact_name: Contact person name
        roi_data: ROI calculation data
    """
    try:
        logger.info(f"Sending ROI report email to {email}...")
        await send_roi_report_email(email, company_name, contact_name, roi_data)
        logger.info(f"✓ ROI report email sent to {email}")
    except Exception as e:
        logger.error(f"✗ Failed to send ROI report email to {email}: {str(e)}")


# ============================================================================
# CALCULATE ROI ENDPOINT
# ============================================================================

@router.post(
    "/calculate",
    response_model=ROICalculationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Calculate ROI",
    description="Calculate ROI based on project and delay data"
)
async def calculate_roi(
    roi_request: ROICalculationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> ROICalculationResponse:
    """
    Calculate ROI for a contractor.
    
    This endpoint:
    - Validates input data
    - Performs ROI calculations
    - Saves calculation to database
    - Updates contractor with ROI data
    - Sends ROI report email asynchronously
    
    **Request Body:**
    - email: Contractor email (required)
    - project_value: Average project value (required)
    - delay_percentage: % of projects with delays (required)
    - projects_per_year: Number of projects per year (required)
    - avg_delay_days: Average delay in days (optional, default: 37)
    - company_size: Company size (optional)
    - industry_focus: Industry focus (optional)
    
    **Returns:**
    - ROICalculationResponse: Calculation results with financial metrics
    
    **Raises:**
    - 404: Contractor not found
    - 400: Invalid data
    - 422: Validation error
    - 500: Database error
    
    **Example:**
    ```
    POST /api/roi/calculate
    {
        "email": "john@abcconstruction.com",
        "project_value": 500000,
        "delay_percentage": 75,
        "projects_per_year": 4,
        "avg_delay_days": 37
    }
    ```
    """
    
    try:
        logger.info(f"Processing ROI calculation for {roi_request.email}")
        
        # Get contractor
        contractor = db.query(Contractor).filter(
            Contractor.email == roi_request.email
        ).first()
        
        if not contractor:
            logger.warning(f"Contractor not found: {roi_request.email}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Contractor with email '{roi_request.email}' not found"
            )
        
        logger.info(f"Found contractor: {contractor.id} ({contractor.company_name})")
        
        # Calculate ROI
        calculator = ROICalculator(settings)
        
        try:
            financial_metrics = calculator.calculate(
                project_value=roi_request.project_value,
                delay_percentage=roi_request.delay_percentage,
                projects_per_year=roi_request.projects_per_year,
                avg_delay_days=roi_request.avg_delay_days
            )
        except ValueError as e:
            logger.error(f"ROI calculation error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid calculation parameters: {str(e)}"
            )
        
        logger.info(f"ROI calculation completed: ROI={financial_metrics['roi_percentage']}%")
        
        # Create ROI calculation record
        roi_calculation = ROICalculation(
            contractor_id=contractor.id,
            project_value=roi_request.project_value,
            delay_percentage=roi_request.delay_percentage,
            projects_per_year=roi_request.projects_per_year,
            avg_delay_days=roi_request.avg_delay_days or settings.avg_project_duration_days,
            annual_delay_cost=financial_metrics['annual_delay_cost'],
            annual_delayed_projects=financial_metrics['annual_delayed_projects'],
            estimated_annual_savings=financial_metrics['estimated_annual_savings'],
            monthly_savings=financial_metrics['monthly_savings'],
            net_annual_benefit=financial_metrics['net_annual_benefit'],
            payback_period_months=financial_metrics['payback_period_months'],
            roi_percentage=financial_metrics['roi_percentage'],
            break_even_months=financial_metrics['break_even_months']
        )
        
        db.add(roi_calculation)
        
        # Update contractor with ROI data
        contractor.estimated_annual_savings = financial_metrics['estimated_annual_savings']
        contractor.roi_percentage = financial_metrics['roi_percentage']
        contractor.payback_period_months = financial_metrics['payback_period_months']
        contractor.roi_report_sent = True
        contractor.last_email_sent_at = datetime.utcnow()
        
        db.commit()
        db.refresh(roi_calculation)
        
        logger.info(f"✓ ROI calculation saved: {roi_calculation.id}")
        
        # Send ROI report email asynchronously
        background_tasks.add_task(
            send_roi_report_email_async,
            roi_request.email,
            contractor.company_name,
            contractor.contact_name,
            financial_metrics
        )
        
        logger.info(f"✓ ROI report email queued for {roi_request.email}")
        
        # Build response
        response_data = {
            "id": roi_calculation.id,
            "contractor_id": roi_calculation.contractor_id,
            "email": contractor.email,
            "project_value": roi_calculation.project_value,
            "delay_percentage": roi_calculation.delay_percentage,
            "projects_per_year": roi_calculation.projects_per_year,
            "avg_delay_days": roi_calculation.avg_delay_days,
            "financial_metrics": financial_metrics,
            "calculation_date": roi_calculation.calculation_date,
            "created_at": roi_calculation.created_at
        }
        
        return ROICalculationResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"✗ Error calculating ROI: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate ROI"
        )


# ============================================================================
# GET ROI SUMMARY ENDPOINT
# ============================================================================

@router.get(
    "/roi-summary/{email}",
    response_model=ROISummaryResponse,
    summary="Get ROI summary",
    description="Get the most recent ROI calculation for a contractor"
)
async def get_roi_summary(
    email: str = Path(..., description="Contractor email address"),
    db: Session = Depends(get_db)
) -> ROISummaryResponse:
    """
    Get ROI summary for a contractor.
    
    Returns the most recent ROI calculation.
    
    **Path Parameters:**
    - email: Contractor email address
    
    **Returns:**
    - ROISummaryResponse: Latest ROI summary
    
    **Raises:**
    - 404: Contractor or ROI calculation not found
    - 500: Database error
    
    **Example:**
    ```
    GET /api/roi/roi-summary/john@abcconstruction.com
    ```
    """
    
    try:
        # Get contractor
        contractor = db.query(Contractor).filter(
            Contractor.email == email
        ).first()
        
        if not contractor:
            logger.warning(f"Contractor not found: {email}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Contractor with email '{email}' not found"
            )
        
        # Get latest ROI calculation
        roi_calculation = db.query(ROICalculation).filter(
            ROICalculation.contractor_id == contractor.id
        ).order_by(
            ROICalculation.calculation_date.desc()
        ).first()
        
        if not roi_calculation:
            logger.warning(f"No ROI calculation found for: {email}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No ROI calculation found for contractor '{email}'"
            )
        
        # Count total calculations
        calculation_count = db.query(func.count(ROICalculation.id)).filter(
            ROICalculation.contractor_id == contractor.id
        ).scalar()
        
        logger.info(f"✓ Retrieved ROI summary for: {email}")
        
        return ROISummaryResponse(
            contractor_id=contractor.id,
            email=contractor.email,
            company_name=contractor.company_name,
            estimated_annual_savings=roi_calculation.estimated_annual_savings,
            roi_percentage=roi_calculation.roi_percentage,
            payback_period_months=roi_calculation.payback_period_months,
            last_calculation_date=roi_calculation.calculation_date,
            calculation_count=calculation_count or 0
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"✗ Error retrieving ROI summary: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve ROI summary"
        )


# ============================================================================
# LIST CALCULATIONS ENDPOINT
# ============================================================================

@router.get(
    "/calculations",
    response_model=ROICalculationListResponse,
    summary="List ROI calculations",
    description="Get a paginated list of ROI calculations"
)
async def list_roi_calculations(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    email: Optional[str] = Query(None, description="Filter by email"),
    db: Session = Depends(get_db)
) -> ROICalculationListResponse:
    """
    List ROI calculations with pagination and filtering.
    
    **Query Parameters:**
    - page: Page number (default: 1)
    - page_size: Items per page (default: 10, max: 100)
    - email: Filter by contractor email
    
    **Returns:**
    - ROICalculationListResponse: Paginated list of calculations
    
    **Example:**
    ```
    GET /api/roi/calculations?page=1&page_size=10
    GET /api/roi/calculations?email=john@abcconstruction.com
    ```
    """
    
    try:
        query = db.query(ROICalculation)
        
        # Apply filters
        if email:
            contractor = db.query(Contractor).filter(
                Contractor.email == email
            ).first()
            
            if contractor:
                query = query.filter(ROICalculation.contractor_id == contractor.id)
            else:
                logger.warning(f"Contractor not found for filter: {email}")
                return ROICalculationListResponse(
                    total=0,
                    count=0,
                    page=page,
                    page_size=page_size,
                    calculations=[]
                )
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        skip = (page - 1) * page_size
        calculations = query.order_by(
            ROICalculation.calculation_date.desc()
        ).offset(skip).limit(page_size).all()
        
        logger.info(f"✓ Listed ROI calculations: page={page}, total={total}")
        
        # Build response with financial metrics
        response_calculations = []
        for calc in calculations:
            contractor = db.query(Contractor).filter(
                Contractor.id == calc.contractor_id
            ).first()
            
            financial_metrics = {
                "annual_delay_cost": calc.annual_delay_cost,
                "annual_delayed_projects": calc.annual_delayed_projects,
                "estimated_annual_savings": calc.estimated_annual_savings,
                "monthly_savings": calc.monthly_savings,
                "ai_solution_annual_cost": settings.ai_solution_annual_cost,
                "net_annual_benefit": calc.net_annual_benefit,
                "payback_period_months": calc.payback_period_months,
                "roi_percentage": calc.roi_percentage,
                "break_even_months": calc.break_even_months
            }
            
            response_calculations.append(ROICalculationResponse(
                id=calc.id,
                contractor_id=calc.contractor_id,
                email=contractor.email if contractor else "unknown",
                project_value=calc.project_value,
                delay_percentage=calc.delay_percentage,
                projects_per_year=calc.projects_per_year,
                avg_delay_days=calc.avg_delay_days,
                financial_metrics=FinancialMetrics(**financial_metrics),
                calculation_date=calc.calculation_date,
                created_at=calc.created_at
            ))
        
        return ROICalculationListResponse(
            total=total,
            count=len(calculations),
            page=page,
            page_size=page_size,
            calculations=response_calculations
        )
        
    except Exception as e:
        logger.error(f"✗ Error listing ROI calculations: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list ROI calculations"
        )


# ============================================================================
# GET CALCULATION BY ID ENDPOINT
# ============================================================================

@router.get(
    "/calculations/{calculation_id}",
    response_model=ROICalculationResponse,
    summary="Get calculation by ID",
    description="Get a specific ROI calculation by ID"
)
async def get_roi_calculation(
    calculation_id: int = Path(..., ge=1, description="Calculation ID"),
    db: Session = Depends(get_db)
) -> ROICalculationResponse:
    """
    Get a ROI calculation by ID.
    
    **Path Parameters:**
    - calculation_id: Calculation ID
    
    **Returns:**
    - ROICalculationResponse: Calculation details
    
    **Raises:**
    - 404: Calculation not found
    - 500: Database error
    
    **Example:**
    ```
    GET /api/roi/calculations/1
    ```
    """
    
    try:
        calculation = db.query(ROICalculation).filter(
            ROICalculation.id == calculation_id
        ).first()
        
        if not calculation:
            logger.warning(f"ROI calculation not found: {calculation_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ROI calculation with id {calculation_id} not found"
            )
        
        contractor = db.query(Contractor).filter(
            Contractor.id == calculation.contractor_id
        ).first()
        
        logger.info(f"✓ Retrieved ROI calculation: {calculation_id}")
        
        financial_metrics = {
            "annual_delay_cost": calculation.annual_delay_cost,
            "annual_delayed_projects": calculation.annual_delayed_projects,
            "estimated_annual_savings": calculation.estimated_annual_savings,
            "monthly_savings": calculation.monthly_savings,
            "ai_solution_annual_cost": settings.ai_solution_annual_cost,
            "net_annual_benefit": calculation.net_annual_benefit,
            "payback_period_months": calculation.payback_period_months,
            "roi_percentage": calculation.roi_percentage,
            "break_even_months": calculation.break_even_months
        }
        
        return ROICalculationResponse(
            id=calculation.id,
            contractor_id=calculation.contractor_id,
            email=contractor.email if contractor else "unknown",
            project_value=calculation.project_value,
            delay_percentage=calculation.delay_percentage,
            projects_per_year=calculation.projects_per_year,
            avg_delay_days=calculation.avg_delay_days,
            financial_metrics=FinancialMetrics(**financial_metrics),
            calculation_date=calculation.calculation_date,
            created_at=calculation.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"✗ Error retrieving ROI calculation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve ROI calculation"
        )


# ============================================================================
# ROI STATISTICS ENDPOINT
# ============================================================================

@router.get(
    "/stats",
    response_model=ROIStatsResponse,
    summary="Get ROI statistics",
    description="Get overview statistics about ROI calculations"
)
async def get_roi_statistics(
    db: Session = Depends(get_db)
) -> ROIStatsResponse:
    """
    Get ROI statistics.
    
    **Returns:**
    - ROIStatsResponse: Statistics overview
    
    **Includes:**
    - Total calculations
    - Average estimated savings
    - Average ROI percentage
    - Total potential savings
    - Number of contractors with ROI
    - Average payback period
    - Highest and lowest ROI
    
    **Example:**
    ```
    GET /api/roi/stats
    ```
    """
    
    try:
        # Get total calculations
        total_calculations = db.query(func.count(ROICalculation.id)).scalar()
        
        # Get contractors with ROI calculations
        contractors_with_roi = db.query(
            func.count(func.distinct(ROICalculation.contractor_id))
        ).scalar()
        
        # Get average estimated savings
        avg_savings = db.query(
            func.avg(ROICalculation.estimated_annual_savings)
        ).scalar()
        
        # Get average ROI percentage
        avg_roi = db.query(
            func.avg(ROICalculation.roi_percentage)
        ).scalar()
        
        # Get total potential savings
        total_savings = db.query(
            func.sum(ROICalculation.estimated_annual_savings)
        ).scalar()
        
        # Get average payback period
        avg_payback = db.query(
            func.avg(ROICalculation.payback_period_months)
        ).scalar()
        
        # Get highest ROI
        highest_roi = db.query(
            func.max(ROICalculation.roi_percentage)
        ).scalar()
        
        # Get lowest ROI
        lowest_roi = db.query(
            func.min(ROICalculation.roi_percentage)
        ).scalar()
        
        logger.info(f"✓ Retrieved ROI statistics")
        
        return ROIStatsResponse(
            total_calculations=total_calculations or 0,
            avg_estimated_savings=avg_savings or 0,
            avg_roi_percentage=avg_roi or 0,
            total_potential_savings=total_savings or 0,
            contractors_with_roi=contractors_with_roi or 0,
            avg_payback_period_months=avg_payback or 0,
            highest_roi_percentage=highest_roi or 0,
            lowest_roi_percentage=lowest_roi or 0
        )
        
    except Exception as e:
        logger.error(f"✗ Error retrieving ROI statistics: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve ROI statistics"
        )


# ============================================================================
# ROUTER INITIALIZATION LOGGING
# ============================================================================

logger.info("ROI calculator routes loaded:")
logger.info("✓ POST /api/roi/calculate - Calculate ROI")
logger.info("✓ GET /api/roi/roi-summary/{email} - Get ROI summary")
logger.info("✓ GET /api/roi/calculations - List calculations")
logger.info("✓ GET /api/roi/calculations/{id} - Get calculation")
logger.info("✓ GET /api/roi/stats - Get statistics")
