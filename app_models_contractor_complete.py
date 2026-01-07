"""
Contractor Models - SQLAlchemy ORM Models for Construction Contractors

This module defines the core models for the Construction AI Landing Page:
- Contractor: Main contractor/company information
- ContactFormSubmission: Track contact form submissions
- ROICalculation: Store ROI calculation results

Features:
- Complete contractor information management
- Contact form submission tracking
- ROI calculation history
- Relationships between models
- Audit trail with timestamps
- Utility methods for common operations
"""

from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, 
    Text, Index, ForeignKey, Enum
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
import enum

from app.database import Base


# ============================================================================
# ENUMS
# ============================================================================

class CompanySizeEnum(str, enum.Enum):
    """Company size enumeration."""
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class ConversionStatusEnum(str, enum.Enum):
    """Conversion status enumeration."""
    LEAD = "lead"
    PROSPECT = "prospect"
    CUSTOMER = "customer"
    LOST = "lost"


class SubmissionStatusEnum(str, enum.Enum):
    """Submission status enumeration."""
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    DISQUALIFIED = "disqualified"


# ============================================================================
# CONTRACTOR MODEL
# ============================================================================

class Contractor(Base):
    """
    Contractor model for storing construction company information.
    
    Stores contractor/company details, engagement status, ROI information,
    and demo booking status.
    
    Attributes:
        id: Unique contractor identifier (primary key)
        company_name: Name of the construction company
        contact_name: Name of the primary contact person
        email: Contact email address (unique)
        phone: Contact phone number
        company_size: Size of company (small, medium, large)
        annual_revenue: Company's annual revenue
        current_challenges: Description of current challenges
        estimated_annual_savings: Estimated annual savings from AI
        roi_percentage: Return on investment percentage
        payback_period_months: Payback period in months
        demo_scheduled: Whether demo is scheduled
        demo_date: Date and time of scheduled demo
        demo_completed: Whether demo was completed
        conversion_status: Lead, prospect, customer, or lost
        welcome_email_sent: Whether welcome email was sent
        roi_report_sent: Whether ROI report was sent
        last_email_sent_at: Timestamp of last email
        notes: Additional notes about contractor
        created_at: Record creation timestamp
        updated_at: Record update timestamp
    
    Relationships:
        contact_form_submissions: One-to-Many with ContactFormSubmission
        roi_calculations: One-to-Many with ROICalculation
        demo_bookings: One-to-Many with DemoBooking
    
    Indexes:
        - email (unique)
        - company_name
        - company_size
        - created_at
        - demo_scheduled
        - conversion_status
    """
    
    __tablename__ = "contractors"
    
    # ========================================================================
    # PRIMARY KEY
    # ========================================================================
    
    id = Column(
        Integer,
        primary_key=True,
        index=True,
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
        doc="Contact email address (unique)"
    )
    
    phone = Column(
        String(20),
        nullable=True,
        doc="Contact phone number"
    )
    
    company_size = Column(
        String(50),
        nullable=True,
        index=True,
        doc="Size of company (small, medium, large)"
    )
    
    annual_revenue = Column(
        Float,
        nullable=True,
        doc="Company's annual revenue"
    )
    
    current_challenges = Column(
        Text,
        nullable=True,
        doc="Description of current challenges"
    )
    
    # ========================================================================
    # ROI INFORMATION
    # ========================================================================
    
    estimated_annual_savings = Column(
        Float,
        nullable=True,
        doc="Estimated annual savings from AI"
    )
    
    roi_percentage = Column(
        Float,
        nullable=True,
        doc="Return on investment percentage"
    )
    
    payback_period_months = Column(
        Float,
        nullable=True,
        doc="Payback period in months"
    )
    
    # ========================================================================
    # DEMO BOOKING
    # ========================================================================
    
    demo_scheduled = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        doc="Whether demo is scheduled"
    )
    
    demo_date = Column(
        DateTime(timezone=True),
        nullable=True,
        doc="Date and time of scheduled demo"
    )
    
    demo_completed = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether demo was completed"
    )
    
    # ========================================================================
    # ENGAGEMENT STATUS
    # ========================================================================
    
    conversion_status = Column(
        String(50),
        default="lead",
        nullable=False,
        index=True,
        doc="Lead, prospect, customer, or lost"
    )
    
    # ========================================================================
    # EMAIL TRACKING
    # ========================================================================
    
    welcome_email_sent = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether welcome email was sent"
    )
    
    roi_report_sent = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether ROI report was sent"
    )
    
    last_email_sent_at = Column(
        DateTime(timezone=True),
        nullable=True,
        doc="Timestamp of last email"
    )
    
    # ========================================================================
    # NOTES
    # ========================================================================
    
    notes = Column(
        Text,
        nullable=True,
        doc="Additional notes about contractor"
    )
    
    # ========================================================================
    # TIMESTAMPS
    # ========================================================================
    
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
        doc="Record creation timestamp"
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
        doc="Record update timestamp"
    )
    
    # ========================================================================
    # RELATIONSHIPS
    # ========================================================================
    
    contact_form_submissions = relationship(
        "ContactFormSubmission",
        back_populates="contractor",
        cascade="all, delete-orphan",
        lazy="select",
        doc="Contact form submissions from this contractor"
    )
    
    roi_calculations = relationship(
        "ROICalculation",
        back_populates="contractor",
        cascade="all, delete-orphan",
        lazy="select",
        doc="ROI calculations for this contractor"
    )
    
    demo_bookings = relationship(
        "DemoBooking",
        back_populates="contractor",
        cascade="all, delete-orphan",
        lazy="select",
        doc="Demo bookings for this contractor"
    )
    
    # ========================================================================
    # INDEXES
    # ========================================================================
    
    __table_args__ = (
        Index("ix_contractor_email", "email", unique=True),
        Index("ix_contractor_company_name", "company_name"),
        Index("ix_contractor_company_size", "company_size"),
        Index("ix_contractor_created_at", "created_at"),
        Index("ix_contractor_demo_scheduled", "demo_scheduled"),
        Index("ix_contractor_conversion_status", "conversion_status"),
    )
    
    # ========================================================================
    # METHODS
    # ========================================================================
    
    def __repr__(self) -> str:
        """String representation of Contractor."""
        return f"<Contractor(id={self.id}, email={self.email}, company={self.company_name})>"
    
    def to_dict(self) -> dict:
        """Convert Contractor object to dictionary."""
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
            "payback_period_months": self.payback_period_months,
            "demo_scheduled": self.demo_scheduled,
            "demo_date": self.demo_date.isoformat() if self.demo_date else None,
            "demo_completed": self.demo_completed,
            "conversion_status": self.conversion_status,
            "welcome_email_sent": self.welcome_email_sent,
            "roi_report_sent": self.roi_report_sent,
            "last_email_sent_at": self.last_email_sent_at.isoformat() if self.last_email_sent_at else None,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    def schedule_demo(self, demo_date: datetime) -> None:
        """Schedule a demo appointment."""
        self.demo_scheduled = True
        self.demo_date = demo_date
        self.updated_at = datetime.now(timezone.utc)
    
    def complete_demo(self) -> None:
        """Mark demo as completed."""
        self.demo_completed = True
        self.updated_at = datetime.now(timezone.utc)
    
    def update_conversion_status(self, status: str) -> None:
        """Update conversion status."""
        if status in [s.value for s in ConversionStatusEnum]:
            self.conversion_status = status
            self.updated_at = datetime.now(timezone.utc)
    
    def set_roi_data(self, savings: float, roi_pct: float, payback_months: float) -> None:
        """Set ROI calculation data."""
        self.estimated_annual_savings = savings
        self.roi_percentage = roi_pct
        self.payback_period_months = payback_months
        self.updated_at = datetime.now(timezone.utc)
    
    def mark_welcome_email_sent(self) -> None:
        """Mark welcome email as sent."""
        self.welcome_email_sent = True
        self.last_email_sent_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
    
    def mark_roi_report_sent(self) -> None:
        """Mark ROI report as sent."""
        self.roi_report_sent = True
        self.last_email_sent_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
    
    def get_submission_count(self) -> int:
        """Get number of contact form submissions."""
        return len(self.contact_form_submissions)
    
    def get_roi_calculation_count(self) -> int:
        """Get number of ROI calculations."""
        return len(self.roi_calculations)
    
    def get_demo_booking_count(self) -> int:
        """Get number of demo bookings."""
        return len(self.demo_bookings)


# ============================================================================
# CONTACT FORM SUBMISSION MODEL
# ============================================================================

class ContactFormSubmission(Base):
    """
    Contact form submission model.
    
    Tracks all contact form submissions from contractors.
    
    Attributes:
        id: Unique submission identifier
        contractor_id: Foreign key to Contractor
        company_name: Company name from submission
        contact_name: Contact name from submission
        email: Email from submission
        phone: Phone from submission
        company_size: Company size from submission
        annual_revenue: Annual revenue from submission
        current_challenges: Challenges from submission
        interested_features: Features interested in
        ip_address: IP address of submitter
        user_agent: User agent of submitter
        referrer: HTTP referrer
        status: Submission status (new, contacted, qualified, disqualified)
        submission_date: Date of submission
        created_at: Record creation timestamp
        updated_at: Record update timestamp
    
    Relationships:
        contractor: Many-to-One with Contractor
    
    Indexes:
        - contractor_id
        - email
        - submission_date
        - status
    """
    
    __tablename__ = "contact_form_submissions"
    
    # ========================================================================
    # PRIMARY KEY
    # ========================================================================
    
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        doc="Unique submission identifier"
    )
    
    # ========================================================================
    # FOREIGN KEY
    # ========================================================================
    
    contractor_id = Column(
        Integer,
        ForeignKey("contractors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Foreign key to Contractor"
    )
    
    # ========================================================================
    # SUBMISSION DATA
    # ========================================================================
    
    company_name = Column(
        String(255),
        nullable=False,
        doc="Company name from submission"
    )
    
    contact_name = Column(
        String(255),
        nullable=False,
        doc="Contact name from submission"
    )
    
    email = Column(
        String(255),
        nullable=False,
        index=True,
        doc="Email from submission"
    )
    
    phone = Column(
        String(20),
        nullable=True,
        doc="Phone from submission"
    )
    
    company_size = Column(
        String(50),
        nullable=True,
        doc="Company size from submission"
    )
    
    annual_revenue = Column(
        Float,
        nullable=True,
        doc="Annual revenue from submission"
    )
    
    current_challenges = Column(
        Text,
        nullable=True,
        doc="Challenges from submission"
    )
    
    interested_features = Column(
        Text,
        nullable=True,
        doc="Features interested in"
    )
    
    # ========================================================================
    # TRACKING DATA
    # ========================================================================
    
    ip_address = Column(
        String(45),
        nullable=True,
        doc="IP address of submitter"
    )
    
    user_agent = Column(
        String(500),
        nullable=True,
        doc="User agent of submitter"
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
        doc="Submission status"
    )
    
    submission_date = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
        doc="Date of submission"
    )
    
    # ========================================================================
    # TIMESTAMPS
    # ========================================================================
    
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        doc="Record creation timestamp"
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
        doc="Record update timestamp"
    )
    
    # ========================================================================
    # RELATIONSHIPS
    # ========================================================================
    
    contractor = relationship(
        "Contractor",
        back_populates="contact_form_submissions",
        doc="Related contractor"
    )
    
    # ========================================================================
    # INDEXES
    # ========================================================================
    
    __table_args__ = (
        Index("ix_submission_contractor_id", "contractor_id"),
        Index("ix_submission_email", "email"),
        Index("ix_submission_submission_date", "submission_date"),
        Index("ix_submission_status", "status"),
    )
    
    # ========================================================================
    # METHODS
    # ========================================================================
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<ContactFormSubmission(id={self.id}, email={self.email})>"
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
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
            "interested_features": self.interested_features,
            "status": self.status,
            "submission_date": self.submission_date.isoformat(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


# ============================================================================
# ROI CALCULATION MODEL
# ============================================================================

class ROICalculation(Base):
    """
    ROI calculation model.
    
    Stores ROI calculation results for contractors.
    
    Attributes:
        id: Unique calculation identifier
        contractor_id: Foreign key to Contractor
        email: Email of contractor
        project_value: Average project value
        delay_percentage: Percentage of projects delayed
        projects_per_year: Number of projects per year
        avg_delay_days: Average delay in days
        annual_delay_cost: Calculated annual delay cost
        estimated_annual_savings: Estimated savings with AI
        monthly_savings: Monthly savings
        ai_solution_annual_cost: Annual cost of AI solution
        net_annual_benefit: Net annual benefit
        payback_period_months: Payback period in months
        roi_percentage: ROI percentage
        break_even_months: Break-even period in months
        calculation_date: Date of calculation
        created_at: Record creation timestamp
    
    Relationships:
        contractor: Many-to-One with Contractor
    
    Indexes:
        - contractor_id
        - calculation_date
    """
    
    __tablename__ = "roi_calculations"
    
    # ========================================================================
    # PRIMARY KEY
    # ========================================================================
    
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        doc="Unique calculation identifier"
    )
    
    # ========================================================================
    # FOREIGN KEY
    # ========================================================================
    
    contractor_id = Column(
        Integer,
        ForeignKey("contractors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Foreign key to Contractor"
    )
    
    # ========================================================================
    # INPUT DATA
    # ========================================================================
    
    email = Column(
        String(255),
        nullable=False,
        doc="Email of contractor"
    )
    
    project_value = Column(
        Float,
        nullable=False,
        doc="Average project value"
    )
    
    delay_percentage = Column(
        Float,
        nullable=False,
        doc="Percentage of projects delayed"
    )
    
    projects_per_year = Column(
        Integer,
        nullable=False,
        doc="Number of projects per year"
    )
    
    avg_delay_days = Column(
        Float,
        nullable=False,
        doc="Average delay in days"
    )
    
    # ========================================================================
    # CALCULATED DATA
    # ========================================================================
    
    annual_delay_cost = Column(
        Float,
        nullable=False,
        doc="Calculated annual delay cost"
    )
    
    estimated_annual_savings = Column(
        Float,
        nullable=False,
        doc="Estimated savings with AI"
    )
    
    monthly_savings = Column(
        Float,
        nullable=False,
        doc="Monthly savings"
    )
    
    ai_solution_annual_cost = Column(
        Float,
        nullable=False,
        doc="Annual cost of AI solution"
    )
    
    net_annual_benefit = Column(
        Float,
        nullable=False,
        doc="Net annual benefit"
    )
    
    payback_period_months = Column(
        Float,
        nullable=False,
        doc="Payback period in months"
    )
    
    roi_percentage = Column(
        Float,
        nullable=False,
        doc="ROI percentage"
    )
    
    break_even_months = Column(
        Float,
        nullable=False,
        doc="Break-even period in months"
    )
    
    # ========================================================================
    # TIMESTAMPS
    # ========================================================================
    
    calculation_date = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
        doc="Date of calculation"
    )
    
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        doc="Record creation timestamp"
    )
    
    # ========================================================================
    # RELATIONSHIPS
    # ========================================================================
    
    contractor = relationship(
        "Contractor",
        back_populates="roi_calculations",
        doc="Related contractor"
    )
    
    # ========================================================================
    # INDEXES
    # ========================================================================
    
    __table_args__ = (
        Index("ix_roi_contractor_id", "contractor_id"),
        Index("ix_roi_calculation_date", "calculation_date"),
    )
    
    # ========================================================================
    # METHODS
    # ========================================================================
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<ROICalculation(id={self.id}, contractor_id={self.contractor_id})>"
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "contractor_id": self.contractor_id,
            "email": self.email,
            "project_value": self.project_value,
            "delay_percentage": self.delay_percentage,
            "projects_per_year": self.projects_per_year,
            "avg_delay_days": self.avg_delay_days,
            "annual_delay_cost": self.annual_delay_cost,
            "estimated_annual_savings": self.estimated_annual_savings,
            "monthly_savings": self.monthly_savings,
            "ai_solution_annual_cost": self.ai_solution_annual_cost,
            "net_annual_benefit": self.net_annual_benefit,
            "payback_period_months": self.payback_period_months,
            "roi_percentage": self.roi_percentage,
            "break_even_months": self.break_even_months,
            "calculation_date": self.calculation_date.isoformat(),
            "created_at": self.created_at.isoformat()
        }


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "Contractor",
    "ContactFormSubmission",
    "ROICalculation",
    "CompanySizeEnum",
    "ConversionStatusEnum",
    "SubmissionStatusEnum"
]
