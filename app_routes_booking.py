"""
Construction AI Landing Page - Demo Booking Routes

This module defines endpoints for demo scheduling:
- GET /api/booking/available-slots - Get available demo time slots
- POST /api/booking/schedule-demo - Schedule a demo appointment
- GET /api/booking/bookings - List all bookings (admin)
- GET /api/booking/bookings/{id} - Get booking details
- PUT /api/booking/bookings/{id} - Update booking status
- DELETE /api/booking/bookings/{id} - Cancel booking
- GET /api/booking/stats - Get booking statistics

Features:
- Generate available time slots (next 14 days, 9am-5pm, weekdays only)
- 30-minute demo slots
- Prevent double-booking
- Save bookings to database
- Send booking confirmation emails
- Track booking status
- Support for rescheduling and cancellation
- Comprehensive error handling
- Database integration with SQLAlchemy

Usage:
    from app.routes.booking import router
    app.include_router(router)
"""

import logging
from typing import Optional, List
from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query, Path, BackgroundTasks, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.database import get_db
from app.models.contractor import Contractor, DemoBooking
from app.config import settings
from app.utils.email import send_booking_confirmation_email, send_booking_reminder_email

# ============================================================================
# ROUTER CONFIGURATION
# ============================================================================

router = APIRouter(
    prefix="/api/booking",
    tags=["booking"],
    responses={
        404: {"description": "Not found"},
        400: {"description": "Bad request"},
        409: {"description": "Conflict - slot already booked"},
        500: {"description": "Internal server error"}
    }
)

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

logger = logging.getLogger(__name__)

# ============================================================================
# CONSTANTS
# ============================================================================

DEMO_DURATION_MINUTES = 30
BUSINESS_HOURS_START = 9  # 9 AM
BUSINESS_HOURS_END = 17   # 5 PM
AVAILABLE_DAYS_AHEAD = 14  # Next 14 days
TIMEZONE = "America/New_York"

# ============================================================================
# SCHEMAS FOR BOOKING ROUTES
# ============================================================================

from pydantic import BaseModel, EmailStr, Field
from enum import Enum

class BookingStatus(str, Enum):
    """Booking status enum."""
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"


class TimeSlot(BaseModel):
    """Schema for available time slot."""
    
    slot_id: str = Field(
        ...,
        description="Unique slot identifier (date-time)"
    )
    
    date: str = Field(
        ...,
        description="Date in YYYY-MM-DD format"
    )
    
    start_time: str = Field(
        ...,
        description="Start time in HH:MM format"
    )
    
    end_time: str = Field(
        ...,
        description="End time in HH:MM format"
    )
    
    available: bool = Field(
        ...,
        description="Whether slot is available"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "slot_id": "2026-01-10-09:00",
                "date": "2026-01-10",
                "start_time": "09:00",
                "end_time": "09:30",
                "available": True
            }
        }


class AvailableSlotsResponse(BaseModel):
    """Schema for available slots response."""
    
    total_slots: int = Field(
        ...,
        description="Total number of slots available"
    )
    
    slots: List[TimeSlot] = Field(
        ...,
        description="List of available time slots"
    )
    
    timezone: str = Field(
        ...,
        description="Timezone for all times"
    )
    
    business_hours: str = Field(
        ...,
        description="Business hours (e.g., '9 AM - 5 PM')"
    )


class ScheduleDemoRequest(BaseModel):
    """Schema for scheduling a demo."""
    
    email: EmailStr = Field(
        ...,
        description="Contractor email address"
    )
    
    slot_id: str = Field(
        ...,
        description="Selected time slot ID (date-time)"
    )
    
    preferred_contact_method: Optional[str] = Field(
        None,
        description="Preferred contact method: phone, email, video"
    )
    
    notes: Optional[str] = Field(
        None,
        max_length=500,
        description="Additional notes or questions"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "john@abcconstruction.com",
                "slot_id": "2026-01-10-09:00",
                "preferred_contact_method": "video",
                "notes": "Interested in project scheduling features"
            }
        }


class DemoBookingResponse(BaseModel):
    """Schema for demo booking response."""
    
    id: int
    contractor_id: int
    email: str
    company_name: str
    contact_name: str
    demo_date: datetime
    demo_time: str
    status: str
    preferred_contact_method: Optional[str]
    notes: Optional[str]
    zoom_link: Optional[str]
    confirmation_sent: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class BookingListResponse(BaseModel):
    """Schema for booking list response."""
    
    total: int
    count: int
    page: int
    page_size: int
    bookings: List[DemoBookingResponse]


class BookingStatsResponse(BaseModel):
    """Schema for booking statistics."""
    
    total_bookings: int
    scheduled: int
    confirmed: int
    completed: int
    cancelled: int
    rescheduled: int
    avg_bookings_per_day: float
    upcoming_bookings: int
    past_bookings: int


# ============================================================================
# BOOKING LOGIC
# ============================================================================

class BookingManager:
    """
    Manages demo booking operations.
    
    Handles time slot generation, availability checking, and booking creation.
    """
    
    def __init__(self, timezone: str = TIMEZONE):
        """
        Initialize booking manager.
        
        Args:
            timezone: Timezone for scheduling (default: America/New_York)
        """
        self.timezone = ZoneInfo(timezone)
        self.demo_duration = timedelta(minutes=DEMO_DURATION_MINUTES)
        self.business_start = BUSINESS_HOURS_START
        self.business_end = BUSINESS_HOURS_END
        self.available_days = AVAILABLE_DAYS_AHEAD
    
    def generate_available_slots(self, db: Session) -> List[dict]:
        """
        Generate available demo slots for the next N days.
        
        Generates 30-minute slots between 9 AM and 5 PM on weekdays.
        Excludes already booked slots.
        
        Args:
            db: Database session
            
        Returns:
            List of available time slots
        """
        
        logger.info("Generating available demo slots...")
        
        slots = []
        now = datetime.now(self.timezone)
        
        # Start from tomorrow at 9 AM
        current_date = now.date() + timedelta(days=1)
        end_date = now.date() + timedelta(days=self.available_days)
        
        logger.debug(f"Generating slots from {current_date} to {end_date}")
        
        while current_date <= end_date:
            # Skip weekends (Monday=0, Sunday=6)
            if current_date.weekday() < 5:  # Monday to Friday
                
                # Generate 30-minute slots for this day
                slot_time = datetime.combine(
                    current_date,
                    time(self.business_start, 0)
                )
                slot_time = self.timezone.localize(slot_time)
                
                while slot_time.hour < self.business_end:
                    slot_end = slot_time + self.demo_duration
                    
                    # Create slot ID
                    slot_id = slot_time.strftime("%Y-%m-%d-%H:%M")
                    
                    # Check if slot is booked
                    booked = db.query(DemoBooking).filter(
                        and_(
                            DemoBooking.demo_date >= slot_time,
                            DemoBooking.demo_date < slot_end,
                            DemoBooking.status != BookingStatus.CANCELLED
                        )
                    ).first()
                    
                    slots.append({
                        "slot_id": slot_id,
                        "date": slot_time.strftime("%Y-%m-%d"),
                        "start_time": slot_time.strftime("%H:%M"),
                        "end_time": slot_end.strftime("%H:%M"),
                        "available": booked is None,
                        "datetime": slot_time
                    })
                    
                    slot_time += self.demo_duration
            
            current_date += timedelta(days=1)
        
        logger.info(f"✓ Generated {len(slots)} total slots")
        
        return slots
    
    def parse_slot_id(self, slot_id: str) -> datetime:
        """
        Parse slot ID to datetime.
        
        Args:
            slot_id: Slot ID in format "YYYY-MM-DD-HH:MM"
            
        Returns:
            Datetime object
            
        Raises:
            ValueError: If slot ID format is invalid
        """
        
        try:
            dt = datetime.strptime(slot_id, "%Y-%m-%d-%H:%M")
            dt = self.timezone.localize(dt)
            return dt
        except ValueError as e:
            logger.error(f"Invalid slot ID format: {slot_id}")
            raise ValueError(f"Invalid slot ID format: {slot_id}") from e
    
    def is_slot_available(self, slot_id: str, db: Session) -> bool:
        """
        Check if a slot is available for booking.
        
        Args:
            slot_id: Slot ID to check
            db: Database session
            
        Returns:
            True if slot is available, False otherwise
        """
        
        try:
            slot_datetime = self.parse_slot_id(slot_id)
            slot_end = slot_datetime + self.demo_duration
            
            # Check for conflicting bookings
            booked = db.query(DemoBooking).filter(
                and_(
                    DemoBooking.demo_date >= slot_datetime,
                    DemoBooking.demo_date < slot_end,
                    DemoBooking.status != BookingStatus.CANCELLED
                )
            ).first()
            
            available = booked is None
            logger.debug(f"Slot {slot_id} available: {available}")
            
            return available
            
        except ValueError as e:
            logger.error(f"Error checking slot availability: {str(e)}")
            return False


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def send_booking_confirmation_email_async(
    email: str,
    company_name: str,
    contact_name: str,
    demo_date: datetime,
    zoom_link: Optional[str] = None
):
    """
    Send booking confirmation email asynchronously.
    
    Args:
        email: Recipient email address
        company_name: Company name
        contact_name: Contact person name
        demo_date: Demo appointment date and time
        zoom_link: Zoom meeting link (optional)
    """
    try:
        logger.info(f"Sending booking confirmation email to {email}...")
        await send_booking_confirmation_email(
            email,
            company_name,
            contact_name,
            demo_date,
            zoom_link
        )
        logger.info(f"✓ Booking confirmation email sent to {email}")
    except Exception as e:
        logger.error(f"✗ Failed to send booking confirmation email to {email}: {str(e)}")


# ============================================================================
# GET AVAILABLE SLOTS ENDPOINT
# ============================================================================

@router.get(
    "/available-slots",
    response_model=AvailableSlotsResponse,
    summary="Get available demo slots",
    description="Get list of available 30-minute demo time slots for the next 14 days"
)
async def get_available_slots(
    db: Session = Depends(get_db)
) -> AvailableSlotsResponse:
    """
    Get available demo time slots.
    
    Returns 30-minute slots for the next 14 days (weekdays only, 9 AM - 5 PM).
    
    **Returns:**
    - AvailableSlotsResponse: List of available time slots
    
    **Slot Details:**
    - Date: YYYY-MM-DD format
    - Time: 30-minute increments
    - Hours: 9 AM to 5 PM
    - Days: Weekdays only (Monday-Friday)
    - Timezone: America/New_York
    
    **Example:**
    ```
    GET /api/booking/available-slots
    ```
    """
    
    try:
        logger.info("Fetching available demo slots...")
        
        # Generate available slots
        booking_manager = BookingManager()
        all_slots = booking_manager.generate_available_slots(db)
        
        # Filter only available slots
        available_slots = [s for s in all_slots if s["available"]]
        
        logger.info(f"✓ Found {len(available_slots)} available slots")
        
        # Build response
        time_slots = [
            TimeSlot(
                slot_id=s["slot_id"],
                date=s["date"],
                start_time=s["start_time"],
                end_time=s["end_time"],
                available=s["available"]
            )
            for s in all_slots
        ]
        
        return AvailableSlotsResponse(
            total_slots=len(available_slots),
            slots=time_slots,
            timezone=TIMEZONE,
            business_hours="9 AM - 5 PM (Weekdays)"
        )
        
    except Exception as e:
        logger.error(f"✗ Error fetching available slots: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch available slots"
        )


# ============================================================================
# SCHEDULE DEMO ENDPOINT
# ============================================================================

@router.post(
    "/schedule-demo",
    response_model=DemoBookingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Schedule a demo",
    description="Schedule a demo appointment for a contractor"
)
async def schedule_demo(
    booking_request: ScheduleDemoRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> DemoBookingResponse:
    """
    Schedule a demo appointment.
    
    This endpoint:
    - Validates contractor email
    - Checks slot availability
    - Creates booking record
    - Updates contractor demo flags
    - Sends confirmation email asynchronously
    - Generates Zoom link (optional)
    
    **Request Body:**
    - email: Contractor email (required)
    - slot_id: Selected time slot ID (required)
    - preferred_contact_method: phone, email, or video (optional)
    - notes: Additional notes (optional)
    
    **Returns:**
    - DemoBookingResponse: Booking details
    
    **Raises:**
    - 404: Contractor not found
    - 409: Slot already booked
    - 400: Invalid slot ID
    - 422: Validation error
    - 500: Database error
    
    **Example:**
    ```
    POST /api/booking/schedule-demo
    {
        "email": "john@abcconstruction.com",
        "slot_id": "2026-01-10-09:00",
        "preferred_contact_method": "video",
        "notes": "Interested in project scheduling"
    }
    ```
    """
    
    try:
        logger.info(f"Processing demo booking for {booking_request.email}")
        
        # Get contractor
        contractor = db.query(Contractor).filter(
            Contractor.email == booking_request.email
        ).first()
        
        if not contractor:
            logger.warning(f"Contractor not found: {booking_request.email}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Contractor with email '{booking_request.email}' not found"
            )
        
        logger.info(f"Found contractor: {contractor.id} ({contractor.company_name})")
        
        # Parse and validate slot ID
        booking_manager = BookingManager()
        
        try:
            demo_datetime = booking_manager.parse_slot_id(booking_request.slot_id)
        except ValueError as e:
            logger.error(f"Invalid slot ID: {booking_request.slot_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid slot ID format: {str(e)}"
            )
        
        logger.debug(f"Parsed slot datetime: {demo_datetime}")
        
        # Check slot availability
        if not booking_manager.is_slot_available(booking_request.slot_id, db):
            logger.warning(f"Slot already booked: {booking_request.slot_id}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Selected time slot is no longer available. Please choose another slot."
            )
        
        logger.info(f"✓ Slot is available: {booking_request.slot_id}")
        
        # Generate Zoom link (placeholder)
        zoom_link = f"https://zoom.us/j/{contractor.id}{demo_datetime.strftime('%Y%m%d%H%M')}"
        
        # Create booking record
        demo_booking = DemoBooking(
            contractor_id=contractor.id,
            demo_date=demo_datetime,
            status=BookingStatus.SCHEDULED,
            preferred_contact_method=booking_request.preferred_contact_method or "video",
            notes=booking_request.notes,
            zoom_link=zoom_link,
            confirmation_sent=False
        )
        
        db.add(demo_booking)
        
        # Update contractor demo flags
        contractor.demo_scheduled = True
        contractor.demo_date = demo_datetime
        contractor.demo_completed = False
        
        db.commit()
        db.refresh(demo_booking)
        
        logger.info(f"✓ Demo booking created: {demo_booking.id}")
        
        # Send confirmation email asynchronously
        background_tasks.add_task(
            send_booking_confirmation_email_async,
            booking_request.email,
            contractor.company_name,
            contractor.contact_name,
            demo_datetime,
            zoom_link
        )
        
        logger.info(f"✓ Booking confirmation email queued for {booking_request.email}")
        
        # Build response
        return DemoBookingResponse(
            id=demo_booking.id,
            contractor_id=demo_booking.contractor_id,
            email=contractor.email,
            company_name=contractor.company_name,
            contact_name=contractor.contact_name,
            demo_date=demo_booking.demo_date,
            demo_time=demo_booking.demo_date.strftime("%H:%M"),
            status=demo_booking.status,
            preferred_contact_method=demo_booking.preferred_contact_method,
            notes=demo_booking.notes,
            zoom_link=demo_booking.zoom_link,
            confirmation_sent=demo_booking.confirmation_sent,
            created_at=demo_booking.created_at,
            updated_at=demo_booking.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"✗ Error scheduling demo: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to schedule demo"
        )


# ============================================================================
# LIST BOOKINGS ENDPOINT
# ============================================================================

@router.get(
    "/bookings",
    response_model=BookingListResponse,
    summary="List demo bookings",
    description="Get a paginated list of demo bookings"
)
async def list_bookings(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    email: Optional[str] = Query(None, description="Filter by email"),
    db: Session = Depends(get_db)
) -> BookingListResponse:
    """
    List demo bookings with pagination and filtering.
    
    **Query Parameters:**
    - page: Page number (default: 1)
    - page_size: Items per page (default: 10, max: 100)
    - status_filter: Filter by status (scheduled, confirmed, completed, cancelled)
    - email: Filter by contractor email
    
    **Returns:**
    - BookingListResponse: Paginated list of bookings
    
    **Example:**
    ```
    GET /api/booking/bookings?page=1&page_size=10
    GET /api/booking/bookings?status_filter=scheduled
    ```
    """
    
    try:
        query = db.query(DemoBooking)
        
        # Apply filters
        if status_filter:
            query = query.filter(DemoBooking.status == status_filter)
        
        if email:
            contractor = db.query(Contractor).filter(
                Contractor.email == email
            ).first()
            
            if contractor:
                query = query.filter(DemoBooking.contractor_id == contractor.id)
            else:
                logger.warning(f"Contractor not found for filter: {email}")
                return BookingListResponse(
                    total=0,
                    count=0,
                    page=page,
                    page_size=page_size,
                    bookings=[]
                )
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        skip = (page - 1) * page_size
        bookings = query.order_by(
            DemoBooking.demo_date.desc()
        ).offset(skip).limit(page_size).all()
        
        logger.info(f"✓ Listed bookings: page={page}, total={total}")
        
        # Build response
        response_bookings = []
        for booking in bookings:
            contractor = db.query(Contractor).filter(
                Contractor.id == booking.contractor_id
            ).first()
            
            response_bookings.append(DemoBookingResponse(
                id=booking.id,
                contractor_id=booking.contractor_id,
                email=contractor.email if contractor else "unknown",
                company_name=contractor.company_name if contractor else "unknown",
                contact_name=contractor.contact_name if contractor else "unknown",
                demo_date=booking.demo_date,
                demo_time=booking.demo_date.strftime("%H:%M"),
                status=booking.status,
                preferred_contact_method=booking.preferred_contact_method,
                notes=booking.notes,
                zoom_link=booking.zoom_link,
                confirmation_sent=booking.confirmation_sent,
                created_at=booking.created_at,
                updated_at=booking.updated_at
            ))
        
        return BookingListResponse(
            total=total,
            count=len(bookings),
            page=page,
            page_size=page_size,
            bookings=response_bookings
        )
        
    except Exception as e:
        logger.error(f"✗ Error listing bookings: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list bookings"
        )


# ============================================================================
# GET BOOKING BY ID ENDPOINT
# ============================================================================

@router.get(
    "/bookings/{booking_id}",
    response_model=DemoBookingResponse,
    summary="Get booking by ID",
    description="Get a specific demo booking by ID"
)
async def get_booking(
    booking_id: int = Path(..., ge=1, description="Booking ID"),
    db: Session = Depends(get_db)
) -> DemoBookingResponse:
    """
    Get a demo booking by ID.
    
    **Path Parameters:**
    - booking_id: Booking ID
    
    **Returns:**
    - DemoBookingResponse: Booking details
    
    **Raises:**
    - 404: Booking not found
    - 500: Database error
    
    **Example:**
    ```
    GET /api/booking/bookings/1
    ```
    """
    
    try:
        booking = db.query(DemoBooking).filter(
            DemoBooking.id == booking_id
        ).first()
        
        if not booking:
            logger.warning(f"Booking not found: {booking_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Booking with id {booking_id} not found"
            )
        
        contractor = db.query(Contractor).filter(
            Contractor.id == booking.contractor_id
        ).first()
        
        logger.info(f"✓ Retrieved booking: {booking_id}")
        
        return DemoBookingResponse(
            id=booking.id,
            contractor_id=booking.contractor_id,
            email=contractor.email if contractor else "unknown",
            company_name=contractor.company_name if contractor else "unknown",
            contact_name=contractor.contact_name if contractor else "unknown",
            demo_date=booking.demo_date,
            demo_time=booking.demo_date.strftime("%H:%M"),
            status=booking.status,
            preferred_contact_method=booking.preferred_contact_method,
            notes=booking.notes,
            zoom_link=booking.zoom_link,
            confirmation_sent=booking.confirmation_sent,
            created_at=booking.created_at,
            updated_at=booking.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"✗ Error retrieving booking: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve booking"
        )


# ============================================================================
# UPDATE BOOKING STATUS ENDPOINT
# ============================================================================

class BookingStatusUpdate(BaseModel):
    """Schema for updating booking status."""
    
    status: str = Field(
        ...,
        description="New status: scheduled, confirmed, completed, cancelled, rescheduled"
    )
    
    notes: Optional[str] = Field(
        None,
        max_length=500,
        description="Notes about the status change"
    )


@router.put(
    "/bookings/{booking_id}",
    response_model=DemoBookingResponse,
    summary="Update booking status",
    description="Update the status of a demo booking"
)
async def update_booking_status(
    booking_id: int = Path(..., ge=1, description="Booking ID"),
    status_update: BookingStatusUpdate = None,
    db: Session = Depends(get_db)
) -> DemoBookingResponse:
    """
    Update booking status.
    
    **Path Parameters:**
    - booking_id: Booking ID
    
    **Request Body:**
    - status: scheduled, confirmed, completed, cancelled, or rescheduled
    - notes: Optional notes
    
    **Returns:**
    - DemoBookingResponse: Updated booking
    
    **Raises:**
    - 404: Booking not found
    - 400: Invalid status
    - 500: Database error
    
    **Example:**
    ```
    PUT /api/booking/bookings/1
    {
        "status": "confirmed",
        "notes": "Contractor confirmed attendance"
    }
    ```
    """
    
    try:
        # Validate status
        valid_statuses = [
            BookingStatus.SCHEDULED,
            BookingStatus.CONFIRMED,
            BookingStatus.COMPLETED,
            BookingStatus.CANCELLED,
            BookingStatus.RESCHEDULED
        ]
        
        if status_update.status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
        
        # Get booking
        booking = db.query(DemoBooking).filter(
            DemoBooking.id == booking_id
        ).first()
        
        if not booking:
            logger.warning(f"Booking not found: {booking_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Booking with id {booking_id} not found"
            )
        
        # Update booking
        booking.status = status_update.status
        if status_update.notes:
            booking.notes = status_update.notes
        booking.updated_at = datetime.utcnow()
        
        # If marking as completed, update contractor flag
        if status_update.status == BookingStatus.COMPLETED:
            contractor = db.query(Contractor).filter(
                Contractor.id == booking.contractor_id
            ).first()
            if contractor:
                contractor.demo_completed = True
        
        db.commit()
        db.refresh(booking)
        
        logger.info(f"✓ Updated booking status: {booking_id} -> {status_update.status}")
        
        contractor = db.query(Contractor).filter(
            Contractor.id == booking.contractor_id
        ).first()
        
        return DemoBookingResponse(
            id=booking.id,
            contractor_id=booking.contractor_id,
            email=contractor.email if contractor else "unknown",
            company_name=contractor.company_name if contractor else "unknown",
            contact_name=contractor.contact_name if contractor else "unknown",
            demo_date=booking.demo_date,
            demo_time=booking.demo_date.strftime("%H:%M"),
            status=booking.status,
            preferred_contact_method=booking.preferred_contact_method,
            notes=booking.notes,
            zoom_link=booking.zoom_link,
            confirmation_sent=booking.confirmation_sent,
            created_at=booking.created_at,
            updated_at=booking.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"✗ Error updating booking: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update booking"
        )


# ============================================================================
# CANCEL BOOKING ENDPOINT
# ============================================================================

@router.delete(
    "/bookings/{booking_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cancel booking",
    description="Cancel a demo booking"
)
async def cancel_booking(
    booking_id: int = Path(..., ge=1, description="Booking ID"),
    db: Session = Depends(get_db)
):
    """
    Cancel a demo booking.
    
    **Path Parameters:**
    - booking_id: Booking ID
    
    **Returns:**
    - 204 No Content
    
    **Raises:**
    - 404: Booking not found
    - 500: Database error
    
    **Example:**
    ```
    DELETE /api/booking/bookings/1
    ```
    """
    
    try:
        # Get booking
        booking = db.query(DemoBooking).filter(
            DemoBooking.id == booking_id
        ).first()
        
        if not booking:
            logger.warning(f"Booking not found: {booking_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Booking with id {booking_id} not found"
            )
        
        # Mark as cancelled instead of deleting
        booking.status = BookingStatus.CANCELLED
        booking.updated_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"✓ Cancelled booking: {booking_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"✗ Error cancelling booking: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel booking"
        )


# ============================================================================
# BOOKING STATISTICS ENDPOINT
# ============================================================================

@router.get(
    "/stats",
    response_model=BookingStatsResponse,
    summary="Get booking statistics",
    description="Get overview statistics about demo bookings"
)
async def get_booking_statistics(
    db: Session = Depends(get_db)
) -> BookingStatsResponse:
    """
    Get booking statistics.
    
    **Returns:**
    - BookingStatsResponse: Statistics overview
    
    **Includes:**
    - Total bookings
    - Breakdown by status
    - Average bookings per day
    - Upcoming and past bookings
    
    **Example:**
    ```
    GET /api/booking/stats
    ```
    """
    
    try:
        now = datetime.utcnow()
        
        # Get total bookings
        total_bookings = db.query(func.count(DemoBooking.id)).scalar()
        
        # Get counts by status
        scheduled = db.query(func.count(DemoBooking.id)).filter(
            DemoBooking.status == BookingStatus.SCHEDULED
        ).scalar()
        
        confirmed = db.query(func.count(DemoBooking.id)).filter(
            DemoBooking.status == BookingStatus.CONFIRMED
        ).scalar()
        
        completed = db.query(func.count(DemoBooking.id)).filter(
            DemoBooking.status == BookingStatus.COMPLETED
        ).scalar()
        
        cancelled = db.query(func.count(DemoBooking.id)).filter(
            DemoBooking.status == BookingStatus.CANCELLED
        ).scalar()
        
        rescheduled = db.query(func.count(DemoBooking.id)).filter(
            DemoBooking.status == BookingStatus.RESCHEDULED
        ).scalar()
        
        # Get upcoming bookings
        upcoming = db.query(func.count(DemoBooking.id)).filter(
            and_(
                DemoBooking.demo_date > now,
                DemoBooking.status != BookingStatus.CANCELLED
            )
        ).scalar()
        
        # Get past bookings
        past = db.query(func.count(DemoBooking.id)).filter(
            and_(
                DemoBooking.demo_date <= now,
                DemoBooking.status != BookingStatus.CANCELLED
            )
        ).scalar()
        
        # Calculate average bookings per day
        avg_per_day = 0.0
        first_booking = db.query(func.min(DemoBooking.created_at)).scalar()
        
        if first_booking:
            days_active = (now - first_booking).days + 1
            avg_per_day = (total_bookings or 0) / days_active if days_active > 0 else 0.0
        
        logger.info(f"✓ Retrieved booking statistics")
        
        return BookingStatsResponse(
            total_bookings=total_bookings or 0,
            scheduled=scheduled or 0,
            confirmed=confirmed or 0,
            completed=completed or 0,
            cancelled=cancelled or 0,
            rescheduled=rescheduled or 0,
            avg_bookings_per_day=avg_per_day,
            upcoming_bookings=upcoming or 0,
            past_bookings=past or 0
        )
        
    except Exception as e:
        logger.error(f"✗ Error retrieving booking statistics: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve booking statistics"
        )


# ============================================================================
# ROUTER INITIALIZATION LOGGING
# ============================================================================

logger.info("Demo booking routes loaded:")
logger.info("✓ GET /api/booking/available-slots - Get available slots")
logger.info("✓ POST /api/booking/schedule-demo - Schedule demo")
logger.info("✓ GET /api/booking/bookings - List bookings")
logger.info("✓ GET /api/booking/bookings/{id} - Get booking")
logger.info("✓ PUT /api/booking/bookings/{id} - Update booking status")
logger.info("✓ DELETE /api/booking/bookings/{id} - Cancel booking")
logger.info("✓ GET /api/booking/stats - Get statistics")
