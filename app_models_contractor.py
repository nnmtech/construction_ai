"""
Construction AI Landing Page - Database Models

This module defines all SQLAlchemy ORM models for the application:
- Contractor: Main contractor/company information
- ContactFormSubmission: Contact form submissions with company details
- ROICalculation: ROI calculations and financial analysis
- DemoBooking: Demo scheduling and booking information

Models include:
- Column definitions with types and constraints
- Relationships between tables
- Timestamps (created_at, updated_at)
- Indexes for query optimization
- String representations for debugging

Usage:
    from app.models.contractor import Contractor, ContactFormSubmission, ROICalculation
    from app.database import SessionLocal
    
    db = SessionLocal()
    contractors = db.query(Contractor).all()
"""

import logging
from datetime import datetime
from typing import Optional, List

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    Index,
    Enum,
    UniqueConstraint,
    CheckConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

logger = logging.getLogger(__name__)

# ============================================================================
# CONTRACTOR MODEL
# ============================================================================

class Contractor(Base):
    """
    Contractor/Company Information Model
    
    Stores information about construction contractors and companies
    that have submitted contact forms or inquired about the AI solution.
    
    Relationships:
    - contact_submissions: One-to-Many with ContactFormSubmission
    - roi_calculations: One-to-Many with ROICalculation
    - demo_bookings: One-to-Many with DemoBooking
    
    Indexes:
    - email (unique)
    - company_name
    - company_size
    - created_at
    """
    
    __tablename__ = "contractor"
    
    # ========================================================================
    # PRIMARY KEY
    # ========================================================================
    
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        doc="Unique contractor identifier"
    )
    
    # ========================================================================
    # COMPANY INFORMATION
    # ========================================================================
    
    company_name = Column(
        String(255),
        nullable=False,
        index=True,
        doc="Name of the construction company"
    )
    
    company_size = Column(
        String(50),
        nullable=True,
        index=True,
        doc="Company size: small, medium, large"
    )
    
    annual_revenue = Column(
        Float,
        nullable=True,
        doc="Annual revenue in dollars"
    )
    
    # ========================================================================
    # CONTACT INFORMATION
    # ========================================================================
    
    contact_name = Column(
        String(255),
        nullable=False,
        doc="Name of the primary contact person"
    )
    
    email = Column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
        doc="Email address (unique identifier)"
    )
    
    phone = Column(
        String(20),
        nullable=True,
        doc="Phone number"
    )
    
    # ========================================================================
    # BUSINESS INFORMATION
    # ========================================================================
    
    current_challenges = Column(
        Text,
        nullable=True,
        doc="Description of current business challenges"
    )
    
    industry_focus = Column(
        String(100),
        nullable=True,
        doc="Primary industry focus (commercial, residential, mixed)"
    )
    
    # ========================================================================
    # AI SOLUTION INFORMATION
    # ========================================================================
    
    estimated_annual_savings = Column(
        Float,
        nullable=True,
        doc="Estimated annual savings with AI solution"
    )
    
    roi_percentage = Column(
        Float,
        nullable=True,
        doc="ROI percentage"
    )
    
    payback_period_months = Column(
        Float,
        nullable=True,
        doc="Payback period in months"
    )
    
    # ========================================================================
    # ENGAGEMENT STATUS
    # ========================================================================
    
    demo_scheduled = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        doc="Whether a demo has been scheduled"
    )
    
    demo_date = Column(
        DateTime,
        nullable=True,
        doc="Scheduled demo date and time"
    )
    
    demo_completed = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether the demo has been completed"
    )
    
    # ========================================================================
    # EMAIL ENGAGEMENT
    # ========================================================================
    
    welcome_email_sent = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether welcome email has been sent"
    )
    
    roi_report_sent = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether ROI report email has been sent"
    )
    
    last_email_sent_at = Column(
        DateTime,
        nullable=True,
        doc="Timestamp of last email sent"
    )
    
    # ========================================================================
    # CONVERSION STATUS
    # ========================================================================
    
    conversion_status = Column(
        String(50),
        default="lead",
        nullable=False,
        index=True,
        doc="Conversion status: lead, prospect, customer, lost"
    )
    
    notes = Column(
        Text,
        nullable=True,
        doc="Internal notes about the contractor"
    )
    
    # ========================================================================
    # TIMESTAMPS
    # ========================================================================
    
    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
        index=True,
        doc="Timestamp when record was created"
    )
    
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="Timestamp when record was last updated"
    )
    
    # ========================================================================
    # RELATIONSHIPS
    # ========================================================================
    
    contact_submissions = relationship(
        "ContactFormSubmission",
        back_populates="contractor",
        cascade="all, delete-orphan",
        doc="Contact form submissions from this contractor"
    )
    
    roi_calculations = relationship(
        "ROICalculation",
        back_populates="contractor",
        cascade="all, delete-orphan",
        doc="ROI calculations for this contractor"
    )
    
    demo_bookings = relationship(
        "DemoBooking",
        back_populates="contractor",
        cascade="all, delete-orphan",
        doc="Demo bookings for this contractor"
    )
    
    # ========================================================================
    # INDEXES
    # ========================================================================
    
    __table_args__ = (
        Index("idx_contractor_email", "email"),
        Index("idx_contractor_company_name", "company_name"),
        Index("idx_contractor_company_size", "company_size"),
        Index("idx_contractor_created_at", "created_at"),
        Index("idx_contractor_demo_scheduled", "demo_scheduled"),
        Index("idx_contractor_conversion_status", "conversion_status"),
        UniqueConstraint("email", name="uq_contractor_email"),
    )
    
    # ========================================================================
    # METHODS
    # ========================================================================
    
    def __repr__(self) -> str:
        """String representation of Contractor."""
        return (
            f"<Contractor(id={self.id}, "
            f"company_name='{self.company_name}', "
            f"email='{self.email}', "
            f"conversion_status='{self.conversion_status}')>"
        )
    
    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "company_name": self.company_name,
            "contact_name": self.contact_name,
            "email": self.email,
            "phone": self.phone,
            "company_size": self.company_size,
            "annual_revenue": self.annual_revenue,
            "current_challenges": self.current_challenges,
            "estimated_annual_savings": self.estimated_annual_savings,
            "roi_percentage": self.roi_percentage,
            "demo_scheduled": self.demo_scheduled,
            "demo_date": self.demo_date.isoformat() if self.demo_date else None,
            "conversion_status": self.conversion_status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


# ============================================================================
# CONTACT FORM SUBMISSION MODEL
# ============================================================================

class ContactFormSubmission(Base):
    """
    Contact Form Submission Model
    
    Tracks all contact form submissions with detailed information
    about the contractor's inquiry and current situation.
    
    Relationships:
    - contractor: Many-to-One with Contractor
    
    Indexes:
    - contractor_id
    - submission_date
    - status
    """
    
    __tablename__ = "contact_form_submission"
    
    # ========================================================================
    # PRIMARY KEY
    # ========================================================================
    
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        doc="Unique submission identifier"
    )
    
    # ========================================================================
    # FOREIGN KEYS
    # ========================================================================
    
    contractor_id = Column(
        Integer,
        ForeignKey("contractor.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Reference to Contractor"
    )
    
    # ========================================================================
    # FORM DATA
    # ========================================================================
    
    company_name = Column(
        String(255),
        nullable=False,
        doc="Company name from form submission"
    )
    
    contact_name = Column(
        String(255),
        nullable=False,
        doc="Contact person name from form"
    )
    
    email = Column(
        String(255),
        nullable=False,
        index=True,
        doc="Email from form submission"
    )
    
    phone = Column(
        String(20),
        nullable=True,
        doc="Phone number from form"
    )
    
    company_size = Column(
        String(50),
        nullable=True,
        doc="Company size: small, medium, large"
    )
    
    annual_revenue = Column(
        Float,
        nullable=True,
        doc="Annual revenue from form"
    )
    
    current_challenges = Column(
        Text,
        nullable=True,
        doc="Current business challenges described in form"
    )
    
    interested_features = Column(
        Text,
        nullable=True,
        doc="Features interested in (comma-separated)"
    )
    
    # ========================================================================
    # SUBMISSION METADATA
    # ========================================================================
    
    ip_address = Column(
        String(45),
        nullable=True,
        doc="IP address of form submitter"
    )
    
    user_agent = Column(
        String(500),
        nullable=True,
        doc="User agent string from browser"
    )
    
    referrer = Column(
        String(500),
        nullable=True,
        doc="HTTP referrer"
    )
    
    # ========================================================================
    # STATUS
    # ========================================================================
    
    status = Column(
        String(50),
        default="new",
        nullable=False,
        index=True,
        doc="Status: new, contacted, qualified, disqualified"
    )
    
    notes = Column(
        Text,
        nullable=True,
        doc="Internal notes about this submission"
    )
    
    # ========================================================================
    # TIMESTAMPS
    # ========================================================================
    
    submission_date = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
        index=True,
        doc="When the form was submitted"
    )
    
    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
        doc="Record creation timestamp"
    )
    
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="Record update timestamp"
    )
    
    # ========================================================================
    # RELATIONSHIPS
    # ========================================================================
    
    contractor = relationship(
        "Contractor",
        back_populates="contact_submissions",
        doc="Reference to parent Contractor"
    )
    
    # ========================================================================
    # INDEXES
    # ========================================================================
    
    __table_args__ = (
        Index("idx_contact_submission_contractor_id", "contractor_id"),
        Index("idx_contact_submission_email", "email"),
        Index("idx_contact_submission_submission_date", "submission_date"),
        Index("idx_contact_submission_status", "status"),
    )
    
    # ========================================================================
    # METHODS
    # ========================================================================
    
    def __repr__(self) -> str:
        """String representation of ContactFormSubmission."""
        return (
            f"<ContactFormSubmission(id={self.id}, "
            f"contractor_id={self.contractor_id}, "
            f"email='{self.email}', "
            f"status='{self.status}')>"
        )
    
    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "contractor_id": self.contractor_id,
            "company_name": self.company_name,
            "contact_name": self.contact_name,
            "email": self.email,
            "phone": self.phone,
            "company_size": self.company_size,
            "annual_revenue": self.annual_revenue,
            "current_challenges": self.current_challenges,
            "status": self.status,
            "submission_date": self.submission_date.isoformat(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


# ============================================================================
# ROI CALCULATION MODEL
# ============================================================================

class ROICalculation(Base):
    """
    ROI Calculation Model
    
    Stores ROI calculations and financial analysis for contractors.
    Tracks the financial impact of the AI solution based on their
    specific project parameters.
    
    Relationships:
    - contractor: Many-to-One with Contractor
    
    Indexes:
    - contractor_id
    - calculation_date
    """
    
    __tablename__ = "roi_calculation"
    
    # ========================================================================
    # PRIMARY KEY
    # ========================================================================
    
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        doc="Unique calculation identifier"
    )
    
    # ========================================================================
    # FOREIGN KEYS
    # ========================================================================
    
    contractor_id = Column(
        Integer,
        ForeignKey("contractor.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Reference to Contractor"
    )
    
    # ========================================================================
    # INPUT PARAMETERS
    # ========================================================================
    
    avg_project_value = Column(
        Float,
        nullable=False,
        doc="Average project value in dollars"
    )
    
    avg_delay_percentage = Column(
        Float,
        nullable=False,
        doc="Average delay percentage (0-100)"
    )
    
    num_projects_per_year = Column(
        Integer,
        nullable=False,
        doc="Number of projects per year"
    )
    
    avg_project_duration_days = Column(
        Integer,
        nullable=True,
        default=180,
        doc="Average project duration in days"
    )
    
    # ========================================================================
    # COST PARAMETERS
    # ========================================================================
    
    cost_per_day_delay = Column(
        Float,
        nullable=False,
        doc="Cost per day of delay in dollars"
    )
    
    ai_solution_annual_cost = Column(
        Float,
        nullable=False,
        doc="Annual cost of AI solution in dollars"
    )
    
    delay_reduction_percentage = Column(
        Float,
        nullable=False,
        doc="Expected delay reduction percentage (0-1)"
    )
    
    # ========================================================================
    # CALCULATED RESULTS
    # ========================================================================
    
    days_delayed_per_project = Column(
        Float,
        nullable=True,
        doc="Calculated days delayed per project"
    )
    
    annual_delay_cost = Column(
        Float,
        nullable=True,
        doc="Calculated annual delay cost in dollars"
    )
    
    estimated_savings_with_ai = Column(
        Float,
        nullable=True,
        doc="Estimated annual savings with AI in dollars"
    )
    
    payback_period_months = Column(
        Float,
        nullable=True,
        doc="Payback period in months"
    )
    
    roi_percentage = Column(
        Float,
        nullable=True,
        doc="ROI percentage"
    )
    
    # ========================================================================
    # ADDITIONAL METRICS
    # ========================================================================
    
    monthly_savings = Column(
        Float,
        nullable=True,
        doc="Estimated monthly savings in dollars"
    )
    
    break_even_months = Column(
        Float,
        nullable=True,
        doc="Months to break even"
    )
    
    three_year_savings = Column(
        Float,
        nullable=True,
        doc="Estimated 3-year savings in dollars"
    )
    
    five_year_savings = Column(
        Float,
        nullable=True,
        doc="Estimated 5-year savings in dollars"
    )
    
    # ========================================================================
    # METADATA
    # ========================================================================
    
    notes = Column(
        Text,
        nullable=True,
        doc="Notes about this calculation"
    )
    
    # ========================================================================
    # TIMESTAMPS
    # ========================================================================
    
    calculation_date = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
        index=True,
        doc="When the calculation was performed"
    )
    
    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
        doc="Record creation timestamp"
    )
    
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="Record update timestamp"
    )
    
    # ========================================================================
    # RELATIONSHIPS
    # ========================================================================
    
    contractor = relationship(
        "Contractor",
        back_populates="roi_calculations",
        doc="Reference to parent Contractor"
    )
    
    # ========================================================================
    # INDEXES
    # ========================================================================
    
    __table_args__ = (
        Index("idx_roi_calculation_contractor_id", "contractor_id"),
        Index("idx_roi_calculation_calculation_date", "calculation_date"),
    )
    
    # ========================================================================
    # METHODS
    # ========================================================================
    
    def __repr__(self) -> str:
        """String representation of ROICalculation."""
        return (
            f"<ROICalculation(id={self.id}, "
            f"contractor_id={self.contractor_id}, "
            f"roi_percentage={self.roi_percentage}%, "
            f"annual_savings=${self.estimated_savings_with_ai:,.0f})>"
        )
    
    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "contractor_id": self.contractor_id,
            "avg_project_value": self.avg_project_value,
            "avg_delay_percentage": self.avg_delay_percentage,
            "num_projects_per_year": self.num_projects_per_year,
            "annual_delay_cost": self.annual_delay_cost,
            "estimated_savings_with_ai": self.estimated_savings_with_ai,
            "payback_period_months": self.payback_period_months,
            "roi_percentage": self.roi_percentage,
            "monthly_savings": self.monthly_savings,
            "three_year_savings": self.three_year_savings,
            "five_year_savings": self.five_year_savings,
            "calculation_date": self.calculation_date.isoformat(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


# ============================================================================
# DEMO BOOKING MODEL
# ============================================================================

class DemoBooking(Base):
    """
    Demo Booking Model
    
    Stores information about scheduled demo sessions with contractors.
    Tracks booking details, status, and follow-up information.
    
    Relationships:
    - contractor: Many-to-One with Contractor
    
    Indexes:
    - contractor_id
    - demo_date
    - status
    """
    
    __tablename__ = "demo_booking"
    
    # ========================================================================
    # PRIMARY KEY
    # ========================================================================
    
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        doc="Unique booking identifier"
    )
    
    # ========================================================================
    # FOREIGN KEYS
    # ========================================================================
    
    contractor_id = Column(
        Integer,
        ForeignKey("contractor.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Reference to Contractor"
    )
    
    # ========================================================================
    # BOOKING DETAILS
    # ========================================================================
    
    demo_date = Column(
        DateTime,
        nullable=False,
        index=True,
        doc="Scheduled date and time of demo"
    )
    
    demo_duration_minutes = Column(
        Integer,
        default=30,
        nullable=False,
        doc="Duration of demo in minutes"
    )
    
    # ========================================================================
    # CONTACT INFORMATION
    # ========================================================================
    
    attendee_name = Column(
        String(255),
        nullable=False,
        doc="Name of person attending demo"
    )
    
    attendee_email = Column(
        String(255),
        nullable=False,
        doc="Email of attendee"
    )
    
    attendee_phone = Column(
        String(20),
        nullable=True,
        doc="Phone number of attendee"
    )
    
    # ========================================================================
    # MEETING DETAILS
    # ========================================================================
    
    meeting_type = Column(
        String(50),
        default="zoom",
        nullable=False,
        doc="Type of meeting: zoom, teams, phone, in_person"
    )
    
    meeting_link = Column(
        String(500),
        nullable=True,
        doc="Meeting link (Zoom, Teams, etc.)"
    )
    
    meeting_password = Column(
        String(50),
        nullable=True,
        doc="Meeting password if required"
    )
    
    # ========================================================================
    # STATUS
    # ========================================================================
    
    status = Column(
        String(50),
        default="scheduled",
        nullable=False,
        index=True,
        doc="Status: scheduled, completed, cancelled, no_show, rescheduled"
    )
    
    cancellation_reason = Column(
        Text,
        nullable=True,
        doc="Reason for cancellation if applicable"
    )
    
    # ========================================================================
    # FOLLOW-UP
    # ========================================================================
    
    demo_completed = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether demo was completed"
    )
    
    demo_feedback = Column(
        Text,
        nullable=True,
        doc="Feedback from demo"
    )
    
    follow_up_required = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether follow-up is required"
    )
    
    follow_up_date = Column(
        DateTime,
        nullable=True,
        doc="Scheduled follow-up date"
    )
    
    # ========================================================================
    # INTERNAL NOTES
    # ========================================================================
    
    notes = Column(
        Text,
        nullable=True,
        doc="Internal notes about the booking"
    )
    
    # ========================================================================
    # TIMESTAMPS
    # ========================================================================
    
    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
        index=True,
        doc="Record creation timestamp"
    )
    
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="Record update timestamp"
    )
    
    # ========================================================================
    # RELATIONSHIPS
    # ========================================================================
    
    contractor = relationship(
        "Contractor",
        back_populates="demo_bookings",
        doc="Reference to parent Contractor"
    )
    
    # ========================================================================
    # INDEXES
    # ========================================================================
    
    __table_args__ = (
        Index("idx_demo_booking_contractor_id", "contractor_id"),
        Index("idx_demo_booking_demo_date", "demo_date"),
        Index("idx_demo_booking_status", "status"),
    )
    
    # ========================================================================
    # METHODS
    # ========================================================================
    
    def __repr__(self) -> str:
        """String representation of DemoBooking."""
        return (
            f"<DemoBooking(id={self.id}, "
            f"contractor_id={self.contractor_id}, "
            f"demo_date={self.demo_date}, "
            f"status='{self.status}')>"
        )
    
    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "contractor_id": self.contractor_id,
            "demo_date": self.demo_date.isoformat(),
            "demo_duration_minutes": self.demo_duration_minutes,
            "attendee_name": self.attendee_name,
            "attendee_email": self.attendee_email,
            "meeting_type": self.meeting_type,
            "meeting_link": self.meeting_link,
            "status": self.status,
            "demo_completed": self.demo_completed,
            "follow_up_required": self.follow_up_required,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


# ============================================================================
# MODEL INITIALIZATION LOGGING
# ============================================================================

logger.info("Database models loaded:")
logger.info("✓ Contractor model")
logger.info("✓ ContactFormSubmission model")
logger.info("✓ ROICalculation model")
logger.info("✓ DemoBooking model")
