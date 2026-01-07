"""
User Model - SQLAlchemy ORM Model for User Authentication

This module defines the User model for storing user account information,
authentication credentials, and email verification status.

Features:
- User account information
- Password hashing
- Email verification
- Account status tracking
- Timestamps for audit trail
- Relationships with other models
- Utility methods for common operations
"""

from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Index, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

from app.database import Base


class User(Base):
    """
    User model for authentication and account management.
    
    Stores user account information including credentials, email verification status,
    and account metadata.
    
    Attributes:
        id: Unique user identifier (primary key)
        company_name: User's company name
        contact_name: User's full name
        email: User's email address (unique)
        password_hash: Hashed password (bcrypt)
        phone: User's phone number
        company_size: Size of company (small, medium, large)
        email_verified: Email verification status
        is_active: Account active status
        created_at: Account creation timestamp
        updated_at: Last update timestamp
        last_login_at: Last login timestamp
    
    Relationships:
        contact_form_submissions: One-to-Many with ContactFormSubmission
        roi_calculations: One-to-Many with ROICalculation
        demo_bookings: One-to-Many with DemoBooking
    
    Indexes:
        - email (unique)
        - email_verified
        - is_active
        - created_at
    """
    
    __tablename__ = "users"
    
    # ========================================================================
    # PRIMARY KEY
    # ========================================================================
    
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        doc="Unique user identifier"
    )
    
    # ========================================================================
    # ACCOUNT INFORMATION
    # ========================================================================
    
    company_name = Column(
        String(255),
        nullable=False,
        index=True,
        doc="User's company name"
    )
    
    contact_name = Column(
        String(255),
        nullable=False,
        doc="User's full name"
    )
    
    email = Column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
        doc="User's email address (unique)"
    )
    
    phone = Column(
        String(20),
        nullable=True,
        doc="User's phone number"
    )
    
    company_size = Column(
        String(50),
        nullable=True,
        doc="Size of company (small, medium, large)"
    )
    
    # ========================================================================
    # AUTHENTICATION
    # ========================================================================
    
    password_hash = Column(
        String(255),
        nullable=False,
        doc="Hashed password (bcrypt)"
    )
    
    # ========================================================================
    # VERIFICATION & STATUS
    # ========================================================================
    
    email_verified = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        doc="Email verification status"
    )
    
    email_verified_at = Column(
        DateTime(timezone=True),
        nullable=True,
        doc="Email verification timestamp"
    )
    
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        doc="Account active status"
    )
    
    # ========================================================================
    # TIMESTAMPS
    # ========================================================================
    
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
        doc="Account creation timestamp"
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
        doc="Last update timestamp"
    )
    
    last_login_at = Column(
        DateTime(timezone=True),
        nullable=True,
        doc="Last login timestamp"
    )
    
    # ========================================================================
    # RELATIONSHIPS
    # ========================================================================
    
    # One-to-Many with ContactFormSubmission
    contact_form_submissions = relationship(
        "ContactFormSubmission",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select",
        doc="User's contact form submissions"
    )
    
    # One-to-Many with ROICalculation
    roi_calculations = relationship(
        "ROICalculation",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select",
        doc="User's ROI calculations"
    )
    
    # One-to-Many with DemoBooking
    demo_bookings = relationship(
        "DemoBooking",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select",
        doc="User's demo bookings"
    )
    
    # ========================================================================
    # INDEXES
    # ========================================================================
    
    __table_args__ = (
        Index("ix_user_email", "email", unique=True),
        Index("ix_user_email_verified", "email_verified"),
        Index("ix_user_is_active", "is_active"),
        Index("ix_user_created_at", "created_at"),
        Index("ix_user_company_name", "company_name"),
    )
    
    # ========================================================================
    # METHODS
    # ========================================================================
    
    def __repr__(self) -> str:
        """String representation of User."""
        return f"<User(id={self.id}, email={self.email}, company={self.company_name})>"
    
    def to_dict(self, include_password: bool = False) -> dict:
        """
        Convert User object to dictionary.
        
        Args:
            include_password: Whether to include password hash (default: False)
        
        Returns:
            Dictionary representation of User
        """
        data = {
            "id": self.id,
            "company_name": self.company_name,
            "contact_name": self.contact_name,
            "email": self.email,
            "phone": self.phone,
            "company_size": self.company_size,
            "email_verified": self.email_verified,
            "email_verified_at": self.email_verified_at.isoformat() if self.email_verified_at else None,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None
        }
        
        if include_password:
            data["password_hash"] = self.password_hash
        
        return data
    
    def mark_email_verified(self) -> None:
        """Mark user's email as verified."""
        self.email_verified = True
        self.email_verified_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
    
    def update_last_login(self) -> None:
        """Update last login timestamp."""
        self.last_login_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
    
    def deactivate(self) -> None:
        """Deactivate user account."""
        self.is_active = False
        self.updated_at = datetime.now(timezone.utc)
    
    def activate(self) -> None:
        """Activate user account."""
        self.is_active = True
        self.updated_at = datetime.now(timezone.utc)
    
    def is_email_verified(self) -> bool:
        """Check if user's email is verified."""
        return self.email_verified
    
    def is_account_active(self) -> bool:
        """Check if user's account is active."""
        return self.is_active
    
    def get_account_age_days(self) -> int:
        """Get account age in days."""
        age = datetime.now(timezone.utc) - self.created_at
        return age.days
    
    def get_days_since_last_login(self) -> Optional[int]:
        """Get days since last login."""
        if not self.last_login_at:
            return None
        days = datetime.now(timezone.utc) - self.last_login_at
        return days.days
    
    def get_submission_count(self) -> int:
        """Get number of contact form submissions."""
        return len(self.contact_form_submissions)
    
    def get_roi_calculation_count(self) -> int:
        """Get number of ROI calculations."""
        return len(self.roi_calculations)
    
    def get_demo_booking_count(self) -> int:
        """Get number of demo bookings."""
        return len(self.demo_bookings)
    
    def get_total_interactions(self) -> int:
        """Get total number of interactions (submissions + ROI + bookings)."""
        return (
            self.get_submission_count() +
            self.get_roi_calculation_count() +
            self.get_demo_booking_count()
        )
    
    @hybrid_property
    def account_age_days(self) -> int:
        """Account age in days (hybrid property for queries)."""
        age = datetime.now(timezone.utc) - self.created_at
        return age.days
    
    @hybrid_property
    def days_since_last_login(self) -> Optional[int]:
        """Days since last login (hybrid property for queries)."""
        if not self.last_login_at:
            return None
        days = datetime.now(timezone.utc) - self.last_login_at
        return days.days


# ============================================================================
# NOTES
# ============================================================================

"""
User Model Integration:

1. Database Initialization:
   - Create user table on app startup
   - Create indexes for performance
   - Enable foreign key constraints

2. Relationships:
   - User → ContactFormSubmission (1:N)
   - User → ROICalculation (1:N)
   - User → DemoBooking (1:N)
   - Cascade delete enabled

3. Authentication:
   - Password stored as bcrypt hash (never plain text)
   - Email verification status tracked
   - Last login timestamp tracked

4. Account Status:
   - Active/inactive status
   - Email verification status
   - Account creation and update timestamps

5. Utility Methods:
   - to_dict(): Convert to dictionary
   - mark_email_verified(): Mark email as verified
   - update_last_login(): Update login timestamp
   - deactivate/activate(): Account status
   - get_*_count(): Get interaction counts
   - Hybrid properties for queries

6. Indexes:
   - email (unique): Fast lookup by email
   - email_verified: Filter verified users
   - is_active: Filter active users
   - created_at: Sort by creation date
   - company_name: Filter by company

7. Usage Examples:

   # Create user
   user = User(
       company_name="ABC Construction",
       contact_name="John Smith",
       email="john@abcconstruction.com",
       password_hash=hash_password("SecurePass123!"),
       company_size="medium"
   )
   db.add(user)
   db.commit()

   # Find user by email
   user = db.query(User).filter_by(email="john@abcconstruction.com").first()

   # Mark email as verified
   user.mark_email_verified()
   db.commit()

   # Update last login
   user.update_last_login()
   db.commit()

   # Get user info
   user_dict = user.to_dict()

   # Get interaction counts
   submissions = user.get_submission_count()
   roi_calcs = user.get_roi_calculation_count()
   bookings = user.get_demo_booking_count()
   total = user.get_total_interactions()

   # Check account status
   if user.is_account_active() and user.is_email_verified():
       # Allow access

   # Get account age
   age = user.get_account_age_days()
   days_since_login = user.get_days_since_last_login()

   # Query by hybrid property
   users = db.query(User).filter(User.account_age_days > 30).all()
"""
