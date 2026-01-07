"""
Construction AI Landing Page - Pydantic Schemas

This module defines Pydantic schemas for request/response validation:
- ContractorBase: Base schema with common fields
- ContractorCreate: Schema for creating contractors
- ContractorUpdate: Schema for updating contractors
- ContractorResponse: Schema for API responses
- ContractorListResponse: Schema for list responses

Usage:
    from fastapi import FastAPI
    from app.schemas.contractor import ContractorCreate, ContractorResponse
    
    @app.post("/contractors", response_model=ContractorResponse)
    async def create_contractor(contractor: ContractorCreate):
        ...
"""

import logging
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

logger = logging.getLogger(__name__)

# ============================================================================
# BASE SCHEMA
# ============================================================================

class ContractorBase(BaseModel):
    """
    Base schema with common contractor fields.
    
    Used as parent for Create and Update schemas.
    """
    
    company_name: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="Name of the construction company"
    )
    
    contact_name: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="Name of the primary contact person"
    )
    
    email: EmailStr = Field(
        ...,
        description="Email address of the contractor"
    )
    
    phone: Optional[str] = Field(
        None,
        max_length=20,
        description="Phone number"
    )
    
    company_size: Optional[str] = Field(
        None,
        description="Company size: small, medium, large"
    )
    
    annual_revenue: Optional[float] = Field(
        None,
        ge=0,
        description="Annual revenue in dollars"
    )
    
    current_challenges: Optional[str] = Field(
        None,
        max_length=2000,
        description="Description of current business challenges"
    )
    
    industry_focus: Optional[str] = Field(
        None,
        description="Primary industry focus: commercial, residential, mixed"
    )
    
    @validator('company_size')
    def validate_company_size(cls, v):
        """Validate company size is one of allowed values."""
        if v is not None and v not in ['small', 'medium', 'large']:
            raise ValueError('company_size must be small, medium, or large')
        return v
    
    @validator('industry_focus')
    def validate_industry_focus(cls, v):
        """Validate industry focus is one of allowed values."""
        if v is not None and v not in ['commercial', 'residential', 'mixed']:
            raise ValueError('industry_focus must be commercial, residential, or mixed')
        return v


# ============================================================================
# CREATE SCHEMA
# ============================================================================

class ContractorCreate(ContractorBase):
    """
    Schema for creating a new contractor.
    
    Inherits all fields from ContractorBase.
    All required fields must be provided.
    """
    
    pass


# ============================================================================
# UPDATE SCHEMA
# ============================================================================

class ContractorUpdate(BaseModel):
    """
    Schema for updating a contractor.
    
    All fields are optional - only provided fields will be updated.
    """
    
    company_name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=255,
        description="Name of the construction company"
    )
    
    contact_name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=255,
        description="Name of the primary contact person"
    )
    
    email: Optional[EmailStr] = Field(
        None,
        description="Email address of the contractor"
    )
    
    phone: Optional[str] = Field(
        None,
        max_length=20,
        description="Phone number"
    )
    
    company_size: Optional[str] = Field(
        None,
        description="Company size: small, medium, large"
    )
    
    annual_revenue: Optional[float] = Field(
        None,
        ge=0,
        description="Annual revenue in dollars"
    )
    
    current_challenges: Optional[str] = Field(
        None,
        max_length=2000,
        description="Description of current business challenges"
    )
    
    industry_focus: Optional[str] = Field(
        None,
        description="Primary industry focus: commercial, residential, mixed"
    )
    
    estimated_annual_savings: Optional[float] = Field(
        None,
        ge=0,
        description="Estimated annual savings with AI solution"
    )
    
    roi_percentage: Optional[float] = Field(
        None,
        ge=0,
        description="ROI percentage"
    )
    
    payback_period_months: Optional[float] = Field(
        None,
        ge=0,
        description="Payback period in months"
    )
    
    demo_scheduled: Optional[bool] = Field(
        None,
        description="Whether a demo has been scheduled"
    )
    
    demo_date: Optional[datetime] = Field(
        None,
        description="Scheduled demo date and time"
    )
    
    demo_completed: Optional[bool] = Field(
        None,
        description="Whether the demo has been completed"
    )
    
    conversion_status: Optional[str] = Field(
        None,
        description="Conversion status: lead, prospect, customer, lost"
    )
    
    notes: Optional[str] = Field(
        None,
        max_length=2000,
        description="Internal notes about the contractor"
    )
    
    @validator('company_size')
    def validate_company_size(cls, v):
        """Validate company size is one of allowed values."""
        if v is not None and v not in ['small', 'medium', 'large']:
            raise ValueError('company_size must be small, medium, or large')
        return v
    
    @validator('industry_focus')
    def validate_industry_focus(cls, v):
        """Validate industry focus is one of allowed values."""
        if v is not None and v not in ['commercial', 'residential', 'mixed']:
            raise ValueError('industry_focus must be commercial, residential, or mixed')
        return v
    
    @validator('conversion_status')
    def validate_conversion_status(cls, v):
        """Validate conversion status is one of allowed values."""
        if v is not None and v not in ['lead', 'prospect', 'customer', 'lost']:
            raise ValueError('conversion_status must be lead, prospect, customer, or lost')
        return v


# ============================================================================
# RESPONSE SCHEMA
# ============================================================================

class ContractorResponse(ContractorBase):
    """
    Schema for contractor API responses.
    
    Includes all fields from ContractorBase plus ID and timestamps.
    """
    
    id: int = Field(
        ...,
        description="Unique contractor identifier"
    )
    
    estimated_annual_savings: Optional[float] = Field(
        None,
        description="Estimated annual savings with AI solution"
    )
    
    roi_percentage: Optional[float] = Field(
        None,
        description="ROI percentage"
    )
    
    payback_period_months: Optional[float] = Field(
        None,
        description="Payback period in months"
    )
    
    demo_scheduled: bool = Field(
        ...,
        description="Whether a demo has been scheduled"
    )
    
    demo_date: Optional[datetime] = Field(
        None,
        description="Scheduled demo date and time"
    )
    
    demo_completed: bool = Field(
        ...,
        description="Whether the demo has been completed"
    )
    
    conversion_status: str = Field(
        ...,
        description="Conversion status: lead, prospect, customer, lost"
    )
    
    welcome_email_sent: bool = Field(
        ...,
        description="Whether welcome email has been sent"
    )
    
    roi_report_sent: bool = Field(
        ...,
        description="Whether ROI report email has been sent"
    )
    
    last_email_sent_at: Optional[datetime] = Field(
        None,
        description="Timestamp of last email sent"
    )
    
    notes: Optional[str] = Field(
        None,
        description="Internal notes about the contractor"
    )
    
    created_at: datetime = Field(
        ...,
        description="Timestamp when record was created"
    )
    
    updated_at: datetime = Field(
        ...,
        description="Timestamp when record was last updated"
    )
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
        json_schema_extra = {
            "example": {
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
                "demo_scheduled": True,
                "demo_date": "2026-01-10T14:00:00",
                "demo_completed": False,
                "conversion_status": "prospect",
                "welcome_email_sent": True,
                "roi_report_sent": False,
                "created_at": "2026-01-05T10:00:00",
                "updated_at": "2026-01-05T10:30:00"
            }
        }


# ============================================================================
# LIST RESPONSE SCHEMA
# ============================================================================

class ContractorListResponse(BaseModel):
    """
    Schema for contractor list API responses.
    
    Includes pagination and list of contractors.
    """
    
    total: int = Field(
        ...,
        description="Total number of contractors"
    )
    
    count: int = Field(
        ...,
        description="Number of contractors in this response"
    )
    
    page: int = Field(
        ...,
        description="Current page number"
    )
    
    page_size: int = Field(
        ...,
        description="Number of items per page"
    )
    
    contractors: List[ContractorResponse] = Field(
        ...,
        description="List of contractors"
    )
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "total": 42,
                "count": 10,
                "page": 1,
                "page_size": 10,
                "contractors": [
                    {
                        "id": 1,
                        "company_name": "ABC Construction",
                        "contact_name": "John Smith",
                        "email": "john@abcconstruction.com",
                        "phone": "404-555-0123",
                        "company_size": "medium",
                        "annual_revenue": 5000000,
                        "current_challenges": "Schedule delays",
                        "industry_focus": "commercial",
                        "estimated_annual_savings": 1000000,
                        "roi_percentage": 200,
                        "demo_scheduled": True,
                        "conversion_status": "prospect",
                        "created_at": "2026-01-05T10:00:00",
                        "updated_at": "2026-01-05T10:30:00"
                    }
                ]
            }
        }


# ============================================================================
# STATISTICS SCHEMA
# ============================================================================

class ContractorStatistics(BaseModel):
    """
    Schema for contractor statistics.
    """
    
    total_contractors: int = Field(
        ...,
        description="Total number of contractors"
    )
    
    leads: int = Field(
        ...,
        description="Number of leads"
    )
    
    prospects: int = Field(
        ...,
        description="Number of prospects"
    )
    
    customers: int = Field(
        ...,
        description="Number of customers"
    )
    
    lost: int = Field(
        ...,
        description="Number of lost leads"
    )
    
    demos_scheduled: int = Field(
        ...,
        description="Number of scheduled demos"
    )
    
    demos_completed: int = Field(
        ...,
        description="Number of completed demos"
    )
    
    avg_estimated_savings: Optional[float] = Field(
        None,
        description="Average estimated annual savings"
    )
    
    avg_roi_percentage: Optional[float] = Field(
        None,
        description="Average ROI percentage"
    )
    
    total_potential_savings: Optional[float] = Field(
        None,
        description="Total potential savings across all contractors"
    )
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
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
        }


# ============================================================================
# ERROR RESPONSE SCHEMA
# ============================================================================

class ErrorResponse(BaseModel):
    """
    Schema for error API responses.
    """
    
    status: str = Field(
        ...,
        description="Error status"
    )
    
    message: str = Field(
        ...,
        description="Error message"
    )
    
    error: Optional[str] = Field(
        None,
        description="Detailed error information"
    )
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "status": "error",
                "message": "Contractor not found",
                "error": "No contractor with id=999"
            }
        }


# ============================================================================
# SCHEMA INITIALIZATION LOGGING
# ============================================================================

logger.info("Contractor schemas loaded:")
logger.info("✓ ContractorBase")
logger.info("✓ ContractorCreate")
logger.info("✓ ContractorUpdate")
logger.info("✓ ContractorResponse")
logger.info("✓ ContractorListResponse")
logger.info("✓ ContractorStatistics")
logger.info("✓ ErrorResponse")
