"""
Construction AI Landing Page - Demo Booking Model

This module defines the SQLAlchemy ORM model for demo bookings.

Models:
- DemoBooking: Stores demo appointment information

Relationships:
- DemoBooking → Contractor (Many-to-One)

Features:
- Automatic timestamps (created_at, updated_at)
- Booking status tracking
- Zoom link storage
- Contact method preferences
- Confirmation tracking
- Comprehensive indexing
- Cascade delete support

Usage:
    from app.models.booking import DemoBooking
    from app.database import SessionLocal
    
    db = SessionLocal()
    booking = db.query(DemoBooking).first()
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    ForeignKey,
    Index,
    Text,
    Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base

# ============================================================================
# ENUMS
# ============================================================================

class BookingStatusEnum:
    """Booking status constants."""
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"
    
    @classmethod
    def all_statuses(cls):
        """Get all valid statuses."""
        return [
            cls.SCHEDULED,
            cls.CONFIRMED,
            cls.COMPLETED,
            cls.CANCELLED,
            cls.RESCHEDULED
        ]


class ContactMethodEnum:
    """Contact method constants."""
    PHONE = "phone"
    EMAIL = "email"
    VIDEO = "video"
    
    @classmethod
    def all_methods(cls):
        """Get all valid contact methods."""
        return [cls.PHONE, cls.EMAIL, cls.VIDEO]


# ============================================================================
# DEMO BOOKING MODEL
# ============================================================================

class DemoBooking(Base):
    """
    SQLAlchemy model for demo bookings.
    
    Stores information about scheduled demo appointments for contractors.
    
    Attributes:
        id (int): Primary key
        contractor_id (int): Foreign key to Contractor
        demo_date (datetime): Date and time of demo appointment
        status (str): Booking status (scheduled, confirmed, completed, cancelled, rescheduled)
        preferred_contact_method (str): Preferred contact method (phone, email, video)
        notes (str): Additional notes or questions
        zoom_link (str): Zoom meeting link
        confirmation_sent (bool): Whether confirmation email was sent
        created_at (datetime): Record creation timestamp
        updated_at (datetime): Record update timestamp
        
    Relationships:
        contractor: Relationship to Contractor model
        
    Indexes:
        - contractor_id: For filtering by contractor
        - demo_date: For sorting by date
        - status: For filtering by status
        - created_at: For sorting by creation date
        - (contractor_id, demo_date): Composite for queries
        - (status, demo_date): Composite for status queries
    """
    
    __tablename__ = "demo_bookings"
    
    # ========================================================================
    # PRIMARY KEY
    # ========================================================================
    
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        doc="Unique booking identifier"
    )
    
    # ========================================================================
    # FOREIGN KEYS
    # ========================================================================
    
    contractor_id = Column(
        Integer,
        ForeignKey("contractors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Foreign key to Contractor"
    )
    
    # ========================================================================
    # BOOKING INFORMATION
    # ========================================================================
    
    demo_date = Column(
        DateTime,
        nullable=False,
        index=True,
        doc="Date and time of demo appointment (UTC)"
    )
    
    status = Column(
        String(50),
        nullable=False,
        default=BookingStatusEnum.SCHEDULED,
        index=True,
        doc="Booking status: scheduled, confirmed, completed, cancelled, rescheduled"
    )
    
    preferred_contact_method = Column(
        String(50),
        nullable=True,
        default=ContactMethodEnum.VIDEO,
        doc="Preferred contact method: phone, email, or video"
    )
    
    notes = Column(
        Text,
        nullable=True,
        doc="Additional notes or questions from contractor"
    )
    
    zoom_link = Column(
        String(500),
        nullable=True,
        doc="Zoom meeting link for video demos"
    )
    
    confirmation_sent = Column(
        Boolean,
        nullable=False,
        default=False,
        doc="Whether confirmation email has been sent"
    )
    
    # ========================================================================
    # TIMESTAMPS
    # ========================================================================
    
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        server_default=func.now(),
        index=True,
        doc="Record creation timestamp (UTC)"
    )
    
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        server_default=func.now(),
        doc="Record update timestamp (UTC)"
    )
    
    # ========================================================================
    # RELATIONSHIPS
    # ========================================================================
    
    contractor = relationship(
        "Contractor",
        back_populates="demo_bookings",
        foreign_keys=[contractor_id],
        lazy="joined",
        doc="Relationship to Contractor model"
    )
    
    # ========================================================================
    # INDEXES
    # ========================================================================
    
    __table_args__ = (
        # Single column indexes
        Index("ix_demo_bookings_contractor_id", "contractor_id"),
        Index("ix_demo_bookings_demo_date", "demo_date"),
        Index("ix_demo_bookings_status", "status"),
        Index("ix_demo_bookings_created_at", "created_at"),
        
        # Composite indexes for common queries
        Index("ix_demo_bookings_contractor_demo_date", "contractor_id", "demo_date"),
        Index("ix_demo_bookings_status_demo_date", "status", "demo_date"),
    )
    
    # ========================================================================
    # METHODS
    # ========================================================================
    
    def __repr__(self) -> str:
        """
        String representation of DemoBooking.
        
        Returns:
            String representation
        """
        return (
            f"<DemoBooking("
            f"id={self.id}, "
            f"contractor_id={self.contractor_id}, "
            f"demo_date={self.demo_date}, "
            f"status={self.status}"
            f")>"
        )
    
    def to_dict(self) -> dict:
        """
        Convert model to dictionary.
        
        Returns:
            Dictionary representation of the model
        """
        return {
            "id": self.id,
            "contractor_id": self.contractor_id,
            "demo_date": self.demo_date.isoformat() if self.demo_date else None,
            "status": self.status,
            "preferred_contact_method": self.preferred_contact_method,
            "notes": self.notes,
            "zoom_link": self.zoom_link,
            "confirmation_sent": self.confirmation_sent,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def is_scheduled(self) -> bool:
        """
        Check if booking is scheduled.
        
        Returns:
            True if status is scheduled, False otherwise
        """
        return self.status == BookingStatusEnum.SCHEDULED
    
    def is_confirmed(self) -> bool:
        """
        Check if booking is confirmed.
        
        Returns:
            True if status is confirmed, False otherwise
        """
        return self.status == BookingStatusEnum.CONFIRMED
    
    def is_completed(self) -> bool:
        """
        Check if booking is completed.
        
        Returns:
            True if status is completed, False otherwise
        """
        return self.status == BookingStatusEnum.COMPLETED
    
    def is_cancelled(self) -> bool:
        """
        Check if booking is cancelled.
        
        Returns:
            True if status is cancelled, False otherwise
        """
        return self.status == BookingStatusEnum.CANCELLED
    
    def is_rescheduled(self) -> bool:
        """
        Check if booking is rescheduled.
        
        Returns:
            True if status is rescheduled, False otherwise
        """
        return self.status == BookingStatusEnum.RESCHEDULED
    
    def is_upcoming(self) -> bool:
        """
        Check if demo is upcoming (in the future).
        
        Returns:
            True if demo_date is in the future, False otherwise
        """
        return self.demo_date > datetime.utcnow()
    
    def is_past(self) -> bool:
        """
        Check if demo is in the past.
        
        Returns:
            True if demo_date is in the past, False otherwise
        """
        return self.demo_date <= datetime.utcnow()
    
    def is_active(self) -> bool:
        """
        Check if booking is active (not cancelled or rescheduled).
        
        Returns:
            True if booking is active, False otherwise
        """
        return self.status not in [
            BookingStatusEnum.CANCELLED,
            BookingStatusEnum.RESCHEDULED
        ]
    
    def can_be_confirmed(self) -> bool:
        """
        Check if booking can be confirmed.
        
        Returns:
            True if booking is scheduled and upcoming, False otherwise
        """
        return self.is_scheduled() and self.is_upcoming()
    
    def can_be_completed(self) -> bool:
        """
        Check if booking can be marked as completed.
        
        Returns:
            True if booking is confirmed or scheduled, False otherwise
        """
        return self.status in [
            BookingStatusEnum.SCHEDULED,
            BookingStatusEnum.CONFIRMED
        ]
    
    def can_be_cancelled(self) -> bool:
        """
        Check if booking can be cancelled.
        
        Returns:
            True if booking is not already cancelled, False otherwise
        """
        return self.status != BookingStatusEnum.CANCELLED
    
    def can_be_rescheduled(self) -> bool:
        """
        Check if booking can be rescheduled.
        
        Returns:
            True if booking is upcoming and not cancelled, False otherwise
        """
        return self.is_upcoming() and self.status != BookingStatusEnum.CANCELLED
    
    def get_status_display(self) -> str:
        """
        Get human-readable status display.
        
        Returns:
            Human-readable status string
        """
        status_map = {
            BookingStatusEnum.SCHEDULED: "Scheduled",
            BookingStatusEnum.CONFIRMED: "Confirmed",
            BookingStatusEnum.COMPLETED: "Completed",
            BookingStatusEnum.CANCELLED: "Cancelled",
            BookingStatusEnum.RESCHEDULED: "Rescheduled"
        }
        return status_map.get(self.status, self.status)
    
    def get_contact_method_display(self) -> str:
        """
        Get human-readable contact method display.
        
        Returns:
            Human-readable contact method string
        """
        method_map = {
            ContactMethodEnum.PHONE: "Phone",
            ContactMethodEnum.EMAIL: "Email",
            ContactMethodEnum.VIDEO: "Video Call"
        }
        return method_map.get(self.preferred_contact_method, self.preferred_contact_method)
    
    def days_until_demo(self) -> int:
        """
        Calculate days until demo.
        
        Returns:
            Number of days until demo (negative if in the past)
        """
        delta = self.demo_date - datetime.utcnow()
        return delta.days
    
    def hours_until_demo(self) -> float:
        """
        Calculate hours until demo.
        
        Returns:
            Number of hours until demo (negative if in the past)
        """
        delta = self.demo_date - datetime.utcnow()
        return delta.total_seconds() / 3600
    
    @classmethod
    def create_from_dict(cls, data: dict) -> "DemoBooking":
        """
        Create DemoBooking instance from dictionary.
        
        Args:
            data: Dictionary with booking data
            
        Returns:
            DemoBooking instance
        """
        return cls(
            contractor_id=data.get("contractor_id"),
            demo_date=data.get("demo_date"),
            status=data.get("status", BookingStatusEnum.SCHEDULED),
            preferred_contact_method=data.get("preferred_contact_method", ContactMethodEnum.VIDEO),
            notes=data.get("notes"),
            zoom_link=data.get("zoom_link"),
            confirmation_sent=data.get("confirmation_sent", False)
        )
    
    # ========================================================================
    # CLASS METHODS FOR COMMON QUERIES
    # ========================================================================
    
    @classmethod
    def get_scheduled_bookings(cls, db_session):
        """
        Get all scheduled bookings.
        
        Args:
            db_session: SQLAlchemy session
            
        Returns:
            Query for scheduled bookings
        """
        return db_session.query(cls).filter(
            cls.status == BookingStatusEnum.SCHEDULED
        )
    
    @classmethod
    def get_upcoming_bookings(cls, db_session):
        """
        Get all upcoming bookings (in the future, not cancelled).
        
        Args:
            db_session: SQLAlchemy session
            
        Returns:
            Query for upcoming bookings
        """
        now = datetime.utcnow()
        return db_session.query(cls).filter(
            (cls.demo_date > now) &
            (cls.status != BookingStatusEnum.CANCELLED)
        )
    
    @classmethod
    def get_past_bookings(cls, db_session):
        """
        Get all past bookings.
        
        Args:
            db_session: SQLAlchemy session
            
        Returns:
            Query for past bookings
        """
        now = datetime.utcnow()
        return db_session.query(cls).filter(
            cls.demo_date <= now
        )
    
    @classmethod
    def get_completed_bookings(cls, db_session):
        """
        Get all completed bookings.
        
        Args:
            db_session: SQLAlchemy session
            
        Returns:
            Query for completed bookings
        """
        return db_session.query(cls).filter(
            cls.status == BookingStatusEnum.COMPLETED
        )
    
    @classmethod
    def get_cancelled_bookings(cls, db_session):
        """
        Get all cancelled bookings.
        
        Args:
            db_session: SQLAlchemy session
            
        Returns:
            Query for cancelled bookings
        """
        return db_session.query(cls).filter(
            cls.status == BookingStatusEnum.CANCELLED
        )
    
    @classmethod
    def get_by_contractor(cls, db_session, contractor_id: int):
        """
        Get all bookings for a contractor.
        
        Args:
            db_session: SQLAlchemy session
            contractor_id: Contractor ID
            
        Returns:
            Query for contractor bookings
        """
        return db_session.query(cls).filter(
            cls.contractor_id == contractor_id
        )
    
    @classmethod
    def get_by_contractor_and_status(cls, db_session, contractor_id: int, status: str):
        """
        Get bookings for a contractor with specific status.
        
        Args:
            db_session: SQLAlchemy session
            contractor_id: Contractor ID
            status: Booking status
            
        Returns:
            Query for contractor bookings with status
        """
        return db_session.query(cls).filter(
            (cls.contractor_id == contractor_id) &
            (cls.status == status)
        )
    
    @classmethod
    def get_by_date_range(cls, db_session, start_date: datetime, end_date: datetime):
        """
        Get bookings within a date range.
        
        Args:
            db_session: SQLAlchemy session
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            
        Returns:
            Query for bookings in date range
        """
        return db_session.query(cls).filter(
            (cls.demo_date >= start_date) &
            (cls.demo_date <= end_date)
        )
    
    @classmethod
    def get_conflicting_bookings(cls, db_session, demo_date: datetime, duration_minutes: int = 30):
        """
        Get bookings that conflict with a given time slot.
        
        Args:
            db_session: SQLAlchemy session
            demo_date: Proposed demo date/time
            duration_minutes: Duration of demo in minutes
            
        Returns:
            Query for conflicting bookings
        """
        from datetime import timedelta
        
        end_time = demo_date + timedelta(minutes=duration_minutes)
        
        return db_session.query(cls).filter(
            (cls.demo_date < end_time) &
            (cls.demo_date + timedelta(minutes=duration_minutes) > demo_date) &
            (cls.status != BookingStatusEnum.CANCELLED)
        )
    
    @classmethod
    def count_by_status(cls, db_session) -> dict:
        """
        Get count of bookings by status.
        
        Args:
            db_session: SQLAlchemy session
            
        Returns:
            Dictionary with status counts
        """
        from sqlalchemy import func
        
        results = db_session.query(
            cls.status,
            func.count(cls.id).label("count")
        ).group_by(cls.status).all()
        
        return {status: count for status, count in results}
    
    @classmethod
    def count_upcoming(cls, db_session) -> int:
        """
        Count upcoming bookings.
        
        Args:
            db_session: SQLAlchemy session
            
        Returns:
            Number of upcoming bookings
        """
        now = datetime.utcnow()
        return db_session.query(cls).filter(
            (cls.demo_date > now) &
            (cls.status != BookingStatusEnum.CANCELLED)
        ).count()
    
    @classmethod
    def count_by_contractor(cls, db_session, contractor_id: int) -> int:
        """
        Count bookings for a contractor.
        
        Args:
            db_session: SQLAlchemy session
            contractor_id: Contractor ID
            
        Returns:
            Number of bookings for contractor
        """
        return db_session.query(cls).filter(
            cls.contractor_id == contractor_id
        ).count()


# ============================================================================
# MODEL DOCUMENTATION
# ============================================================================

"""
DemoBooking Model Usage Examples
=================================

1. Create a new booking:
    
    booking = DemoBooking(
        contractor_id=1,
        demo_date=datetime(2026, 1, 10, 9, 0),
        status="scheduled",
        preferred_contact_method="video",
        zoom_link="https://zoom.us/j/123456789"
    )
    db.add(booking)
    db.commit()

2. Get upcoming bookings:
    
    upcoming = DemoBooking.get_upcoming_bookings(db).all()
    for booking in upcoming:
        print(f"{booking.contractor.company_name}: {booking.demo_date}")

3. Update booking status:
    
    booking = db.query(DemoBooking).filter_by(id=1).first()
    booking.status = "confirmed"
    db.commit()

4. Check for conflicts:
    
    proposed_time = datetime(2026, 1, 10, 9, 0)
    conflicts = DemoBooking.get_conflicting_bookings(db, proposed_time).all()
    if conflicts:
        print("Slot is already booked")

5. Get booking statistics:
    
    stats = DemoBooking.count_by_status(db)
    print(f"Scheduled: {stats.get('scheduled', 0)}")
    print(f"Confirmed: {stats.get('confirmed', 0)}")

6. Filter by contractor:
    
    contractor_bookings = DemoBooking.get_by_contractor(db, contractor_id=1).all()
    for booking in contractor_bookings:
        print(f"{booking.status}: {booking.demo_date}")

7. Get bookings in date range:
    
    start = datetime(2026, 1, 1)
    end = datetime(2026, 1, 31)
    bookings = DemoBooking.get_by_date_range(db, start, end).all()

8. Check booking state:
    
    booking = db.query(DemoBooking).filter_by(id=1).first()
    if booking.is_upcoming():
        print("Demo is upcoming")
    if booking.can_be_confirmed():
        print("Demo can be confirmed")
    if booking.can_be_rescheduled():
        print("Demo can be rescheduled")

9. Get human-readable display:
    
    booking = db.query(DemoBooking).filter_by(id=1).first()
    print(f"Status: {booking.get_status_display()}")
    print(f"Contact: {booking.get_contact_method_display()}")
    print(f"Days until demo: {booking.days_until_demo()}")

10. Convert to dictionary:
    
    booking = db.query(DemoBooking).filter_by(id=1).first()
    booking_dict = booking.to_dict()
    return booking_dict
"""
