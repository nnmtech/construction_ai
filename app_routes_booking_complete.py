"""
Construction AI Landing Page - Demo Booking Routes

This module defines FastAPI routes for demo scheduling and booking management.

Endpoints:
- GET /api/booking/available-slots - Get available demo time slots
- POST /api/booking/schedule-demo - Schedule a demo appointment
- GET /api/booking/bookings - List all bookings (paginated)
- GET /api/booking/bookings/{booking_id} - Get booking details
- PUT /api/booking/bookings/{booking_id} - Update booking status
- DELETE /api/booking/bookings/{booking_id} - Cancel booking
- GET /api/booking/stats - Get booking statistics

Features:
- Automatic slot generation (30-minute intervals)
- Conflict detection and prevention
- Zoom link generation
- Email automation
- Comprehensive error handling
- Pagination support
- Status tracking
- Logging

Usage:
    from app.routes import booking
    
    app.include_router(booking.router)
"""

from datetime import datetime, timedelta
from typing import List, Optional
import logging
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.database import get_db
from app.models.contractor import Contractor
from app.models.booking import DemoBooking, BookingStatusEnum, ContactMethodEnum
from app.schemas.booking import (
    TimeSlot,
    AvailableSlotsResponse,
    ScheduleDemoRequest,
    DemoBookingResponse,
    BookingListResponse,
    BookingStatusUpdate,
    BookingStatsResponse
)
from app.utils.email import send_demo_confirmation_email

# ============================================================================
# CONFIGURATION
# ============================================================================

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/booking", tags=["booking"])

# Demo scheduling configuration
DEMO_DURATION_MINUTES = 30
BUSINESS_HOURS_START = 9  # 9 AM
BUSINESS_HOURS_END = 17   # 5 PM
AVAILABLE_DAYS_AHEAD = 14
TIMEZONE = ZoneInfo("America/New_York")

# ============================================================================
# BOOKING MANAGER CLASS
# ============================================================================

class BookingManager:
    """Manages demo booking logic and slot generation."""
    
    @staticmethod
    def generate_available_slots(db: Session) -> List[dict]:
        """
        Generate available demo slots for the next 14 days.
        
        Generates 30-minute slots for weekdays (Mon-Fri) from 9 AM to 5 PM EST.
        Checks for existing bookings and marks slots as unavailable if booked.
        
        Args:
            db: SQLAlchemy database session
            
        Returns:
            List of slot dictionaries with:
            - slot_id: Unique slot identifier (YYYY-MM-DD-HH:MM)
            - date: Date string (YYYY-MM-DD)
            - start_time: Start time (HH:MM)
            - end_time: End time (HH:MM)
            - available: Boolean indicating availability
        """
        slots = []
        now = datetime.now(TIMEZONE)
        
        # Generate slots for the next 14 days
        for day_offset in range(AVAILABLE_DAYS_AHEAD):
            slot_date = now + timedelta(days=day_offset)
            
            # Skip weekends (5=Saturday, 6=Sunday)
            if slot_date.weekday() >= 5:
                continue
            
            # Generate 30-minute slots for business hours
            for hour in range(BUSINESS_HOURS_START, BUSINESS_HOURS_END):
                for minute in [0, 30]:
                    slot_start = slot_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    slot_end = slot_start + timedelta(minutes=DEMO_DURATION_MINUTES)
                    
                    # Skip if slot end time is after business hours
                    if slot_end.hour > BUSINESS_HOURS_END:
                        continue
                    
                    # Check if slot is already booked
                    conflicts = DemoBooking.get_conflicting_bookings(
                        db, 
                        slot_start, 
                        DEMO_DURATION_MINUTES
                    ).count()
                    
                    slot_id = slot_start.strftime("%Y-%m-%d-%H:%M")
                    
                    slots.append({
                        "slot_id": slot_id,
                        "date": slot_start.strftime("%Y-%m-%d"),
                        "start_time": slot_start.strftime("%H:%M"),
                        "end_time": slot_end.strftime("%H:%M"),
                        "available": conflicts == 0,
                        "datetime": slot_start
                    })
        
        return slots
    
    @staticmethod
    def parse_slot_id(slot_id: str) -> datetime:
        """
        Parse slot ID to datetime.
        
        Args:
            slot_id: Slot ID in format "YYYY-MM-DD-HH:MM"
            
        Returns:
            Datetime object in EST timezone
            
        Raises:
            ValueError: If slot ID format is invalid
        """
        try:
            dt = datetime.strptime(slot_id, "%Y-%m-%d-%H:%M")
            return dt.replace(tzinfo=TIMEZONE)
        except ValueError as e:
            raise ValueError(f"Invalid slot ID format: {str(e)}")
    
    @staticmethod
    def is_slot_available(slot_id: str, db: Session) -> bool:
        """
        Check if a slot is available for booking.
        
        Args:
            slot_id: Slot ID to check
            db: SQLAlchemy database session
            
        Returns:
            True if available, False otherwise
        """
        try:
            slot_datetime = BookingManager.parse_slot_id(slot_id)
            conflicts = DemoBooking.get_conflicting_bookings(
                db,
                slot_datetime,
                DEMO_DURATION_MINUTES
            ).count()
            return conflicts == 0
        except ValueError:
            return False
    
    @staticmethod
    def generate_zoom_link(contractor_id: int, booking_id: int) -> str:
        """
        Generate a Zoom meeting link.
        
        In production, this would integrate with Zoom API.
        For now, returns a placeholder link.
        
        Args:
            contractor_id: Contractor ID
            booking_id: Booking ID
            
        Returns:
            Zoom meeting link
        """
        # Placeholder: In production, integrate with Zoom API
        zoom_meeting_id = f"{contractor_id}{booking_id:06d}"
        return f"https://zoom.us/j/{zoom_meeting_id}"

# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get(
    "/available-slots",
    response_model=AvailableSlotsResponse,
    summary="Get Available Demo Slots",
    description="Get available demo time slots for the next 14 days (9 AM - 5 PM EST, weekdays only)"
)
async def get_available_slots(db: Session = Depends(get_db)):
    """
    Get available demo time slots.
    
    Returns 30-minute slots for the next 14 days, weekdays only, 9 AM - 5 PM EST.
    Automatically checks for conflicts and marks slots as unavailable if booked.
    
    Returns:
        AvailableSlotsResponse with list of available and unavailable slots
    """
    try:
        logger.info("Generating available demo slots")
        
        slots = BookingManager.generate_available_slots(db)
        
        logger.info(f"Generated {len(slots)} total slots")
        
        return AvailableSlotsResponse(
            total_slots=len(slots),
            slots=[
                TimeSlot(
                    slot_id=slot["slot_id"],
                    date=slot["date"],
                    start_time=slot["start_time"],
                    end_time=slot["end_time"],
                    available=slot["available"]
                )
                for slot in slots
            ],
            timezone="America/New_York",
            business_hours="9 AM - 5 PM (Weekdays)"
        )
    
    except Exception as e:
        logger.error(f"Error generating slots: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate available slots"
        )


@router.post(
    "/schedule-demo",
    response_model=DemoBookingResponse,
    status_code=201,
    summary="Schedule a Demo",
    description="Schedule a demo appointment for a contractor"
)
async def schedule_demo(
    request: ScheduleDemoRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Schedule a demo appointment.
    
    Validates contractor email, checks slot availability, creates booking,
    and sends confirmation email asynchronously.
    
    Args:
        request: ScheduleDemoRequest with email, slot_id, and contact method
        background_tasks: FastAPI background tasks
        db: SQLAlchemy database session
        
    Returns:
        DemoBookingResponse with booking details
        
    Raises:
        HTTPException: If contractor not found, slot invalid, or already booked
    """
    try:
        logger.info(f"Scheduling demo for {request.email}")
        
        # ====================================================================
        # VALIDATE CONTRACTOR
        # ====================================================================
        
        contractor = db.query(Contractor).filter(
            Contractor.email == request.email
        ).first()
        
        if not contractor:
            logger.warning(f"Contractor not found: {request.email}")
            raise HTTPException(
                status_code=404,
                detail=f"Contractor with email '{request.email}' not found"
            )
        
        logger.info(f"Found contractor: {contractor.company_name}")
        
        # ====================================================================
        # VALIDATE SLOT ID
        # ====================================================================
        
        try:
            slot_datetime = BookingManager.parse_slot_id(request.slot_id)
        except ValueError as e:
            logger.error(f"Invalid slot ID: {request.slot_id}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid slot ID format: {str(e)}"
            )
        
        logger.info(f"Parsed slot datetime: {slot_datetime}")
        
        # ====================================================================
        # CHECK SLOT AVAILABILITY
        # ====================================================================
        
        if not BookingManager.is_slot_available(request.slot_id, db):
            logger.warning(f"Slot already booked: {request.slot_id}")
            raise HTTPException(
                status_code=409,
                detail="Selected time slot is no longer available. Please choose another slot."
            )
        
        logger.info(f"Slot is available: {request.slot_id}")
        
        # ====================================================================
        # CREATE BOOKING
        # ====================================================================
        
        # Generate Zoom link
        zoom_link = BookingManager.generate_zoom_link(contractor.id, 0)
        
        # Create booking record
        booking = DemoBooking(
            contractor_id=contractor.id,
            demo_date=slot_datetime,
            status=BookingStatusEnum.SCHEDULED,
            preferred_contact_method=request.preferred_contact_method or ContactMethodEnum.VIDEO,
            notes=request.notes,
            zoom_link=zoom_link,
            confirmation_sent=False
        )
        
        db.add(booking)
        db.flush()  # Get booking ID before commit
        
        # Update Zoom link with booking ID
        booking.zoom_link = BookingManager.generate_zoom_link(contractor.id, booking.id)
        
        # ====================================================================
        # UPDATE CONTRACTOR
        # ====================================================================
        
        contractor.demo_scheduled = True
        contractor.demo_date = slot_datetime
        contractor.demo_completed = False
        
        db.commit()
        db.refresh(booking)
        
        logger.info(f"Booking created: ID={booking.id}")
        
        # ====================================================================
        # SEND CONFIRMATION EMAIL (ASYNC)
        # ====================================================================
        
        background_tasks.add_task(
            send_demo_confirmation_email,
            contractor=contractor,
            booking=booking
        )
        
        logger.info(f"Confirmation email queued for {contractor.email}")
        
        # ====================================================================
        # RETURN RESPONSE
        # ====================================================================
        
        return DemoBookingResponse(
            id=booking.id,
            contractor_id=booking.contractor_id,
            email=contractor.email,
            company_name=contractor.company_name,
            contact_name=contractor.contact_name,
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
        logger.error(f"Error scheduling demo: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to schedule demo"
        )


@router.get(
    "/bookings",
    response_model=BookingListResponse,
    summary="List Bookings",
    description="Get paginated list of demo bookings"
)
async def list_bookings(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    email: Optional[str] = Query(None, description="Filter by contractor email"),
    db: Session = Depends(get_db)
):
    """
    List demo bookings with pagination and filtering.
    
    Args:
        page: Page number (default: 1)
        page_size: Items per page (default: 10, max: 100)
        status_filter: Filter by status (optional)
        email: Filter by contractor email (optional)
        db: SQLAlchemy database session
        
    Returns:
        BookingListResponse with paginated bookings
    """
    try:
        logger.info(f"Listing bookings: page={page}, page_size={page_size}")
        
        # Build query
        query = db.query(DemoBooking)
        
        # Apply filters
        if status_filter:
            if status_filter not in BookingStatusEnum.all_statuses():
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid status. Must be one of: {', '.join(BookingStatusEnum.all_statuses())}"
                )
            query = query.filter(DemoBooking.status == status_filter)
        
        if email:
            query = query.join(Contractor).filter(Contractor.email == email)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * page_size
        bookings = query.order_by(DemoBooking.demo_date.desc()).offset(offset).limit(page_size).all()
        
        logger.info(f"Found {total} bookings, returning {len(bookings)}")
        
        return BookingListResponse(
            total=total,
            count=len(bookings),
            page=page,
            page_size=page_size,
            bookings=[
                DemoBookingResponse(
                    id=booking.id,
                    contractor_id=booking.contractor_id,
                    email=booking.contractor.email,
                    company_name=booking.contractor.company_name,
                    contact_name=booking.contractor.contact_name,
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
                for booking in bookings
            ]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing bookings: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to list bookings"
        )


@router.get(
    "/bookings/{booking_id}",
    response_model=DemoBookingResponse,
    summary="Get Booking Details",
    description="Get details of a specific demo booking"
)
async def get_booking(
    booking_id: int,
    db: Session = Depends(get_db)
):
    """
    Get details of a specific booking.
    
    Args:
        booking_id: Booking ID
        db: SQLAlchemy database session
        
    Returns:
        DemoBookingResponse with booking details
        
    Raises:
        HTTPException: If booking not found
    """
    try:
        logger.info(f"Getting booking: {booking_id}")
        
        booking = db.query(DemoBooking).filter(
            DemoBooking.id == booking_id
        ).first()
        
        if not booking:
            logger.warning(f"Booking not found: {booking_id}")
            raise HTTPException(
                status_code=404,
                detail=f"Booking with id {booking_id} not found"
            )
        
        logger.info(f"Found booking: {booking_id}")
        
        return DemoBookingResponse(
            id=booking.id,
            contractor_id=booking.contractor_id,
            email=booking.contractor.email,
            company_name=booking.contractor.company_name,
            contact_name=booking.contractor.contact_name,
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
        logger.error(f"Error getting booking: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get booking"
        )


@router.put(
    "/bookings/{booking_id}",
    response_model=DemoBookingResponse,
    summary="Update Booking Status",
    description="Update the status of a demo booking"
)
async def update_booking(
    booking_id: int,
    request: BookingStatusUpdate,
    db: Session = Depends(get_db)
):
    """
    Update booking status.
    
    Args:
        booking_id: Booking ID
        request: BookingStatusUpdate with new status
        db: SQLAlchemy database session
        
    Returns:
        DemoBookingResponse with updated booking
        
    Raises:
        HTTPException: If booking not found or invalid status
    """
    try:
        logger.info(f"Updating booking: {booking_id} to status: {request.status}")
        
        # Validate status
        if request.status not in BookingStatusEnum.all_statuses():
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be one of: {', '.join(BookingStatusEnum.all_statuses())}"
            )
        
        # Get booking
        booking = db.query(DemoBooking).filter(
            DemoBooking.id == booking_id
        ).first()
        
        if not booking:
            logger.warning(f"Booking not found: {booking_id}")
            raise HTTPException(
                status_code=404,
                detail=f"Booking with id {booking_id} not found"
            )
        
        # Update status
        booking.status = request.status
        if request.notes:
            booking.notes = request.notes
        
        db.commit()
        db.refresh(booking)
        
        logger.info(f"Booking updated: {booking_id}")
        
        return DemoBookingResponse(
            id=booking.id,
            contractor_id=booking.contractor_id,
            email=booking.contractor.email,
            company_name=booking.contractor.company_name,
            contact_name=booking.contractor.contact_name,
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
        logger.error(f"Error updating booking: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to update booking"
        )


@router.delete(
    "/bookings/{booking_id}",
    status_code=204,
    summary="Cancel Booking",
    description="Cancel a demo booking"
)
async def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db)
):
    """
    Cancel a booking.
    
    Args:
        booking_id: Booking ID
        db: SQLAlchemy database session
        
    Raises:
        HTTPException: If booking not found
    """
    try:
        logger.info(f"Cancelling booking: {booking_id}")
        
        booking = db.query(DemoBooking).filter(
            DemoBooking.id == booking_id
        ).first()
        
        if not booking:
            logger.warning(f"Booking not found: {booking_id}")
            raise HTTPException(
                status_code=404,
                detail=f"Booking with id {booking_id} not found"
            )
        
        booking.status = BookingStatusEnum.CANCELLED
        db.commit()
        
        logger.info(f"Booking cancelled: {booking_id}")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling booking: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to cancel booking"
        )


@router.get(
    "/stats",
    response_model=BookingStatsResponse,
    summary="Get Booking Statistics",
    description="Get aggregated booking statistics"
)
async def get_booking_stats(db: Session = Depends(get_db)):
    """
    Get booking statistics.
    
    Returns aggregated statistics about all bookings.
    
    Args:
        db: SQLAlchemy database session
        
    Returns:
        BookingStatsResponse with statistics
    """
    try:
        logger.info("Getting booking statistics")
        
        # Get status counts
        status_counts = DemoBooking.count_by_status(db)
        
        # Get total count
        total = db.query(func.count(DemoBooking.id)).scalar()
        
        # Get upcoming count
        upcoming = DemoBooking.count_upcoming(db)
        
        # Get past count
        now = datetime.utcnow()
        past = db.query(func.count(DemoBooking.id)).filter(
            DemoBooking.demo_date <= now
        ).scalar()
        
        # Calculate average bookings per day
        days_with_bookings = db.query(
            func.count(func.distinct(func.date(DemoBooking.demo_date)))
        ).filter(
            DemoBooking.status != BookingStatusEnum.CANCELLED
        ).scalar() or 1
        
        avg_per_day = total / days_with_bookings if days_with_bookings > 0 else 0
        
        logger.info(f"Total bookings: {total}, Upcoming: {upcoming}, Past: {past}")
        
        return BookingStatsResponse(
            total_bookings=total or 0,
            scheduled=status_counts.get(BookingStatusEnum.SCHEDULED, 0),
            confirmed=status_counts.get(BookingStatusEnum.CONFIRMED, 0),
            completed=status_counts.get(BookingStatusEnum.COMPLETED, 0),
            cancelled=status_counts.get(BookingStatusEnum.CANCELLED, 0),
            rescheduled=status_counts.get(BookingStatusEnum.RESCHEDULED, 0),
            avg_bookings_per_day=round(avg_per_day, 2),
            upcoming_bookings=upcoming,
            past_bookings=past or 0
        )
    
    except Exception as e:
        logger.error(f"Error getting booking stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get booking statistics"
        )
