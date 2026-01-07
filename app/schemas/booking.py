"""Booking-related Pydantic schemas.

These schemas are referenced by `app_routes_booking_complete.py`.
They are intentionally lightweight and align to the fields used in that module.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class TimeSlot(BaseModel):
    slot_id: str
    date: str
    start_time: str
    end_time: str
    available: bool


class AvailableSlotsResponse(BaseModel):
    available_slots: List[TimeSlot]


class ScheduleDemoRequest(BaseModel):
    email: EmailStr
    slot_id: str = Field(..., description="Slot identifier (YYYY-MM-DD-HH:MM)")
    preferred_contact_method: Optional[str] = Field(None, description="video|phone|email")
    notes: Optional[str] = None


class DemoBookingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    contractor_id: int
    email: str
    company_name: str
    contact_name: str
    demo_date: datetime
    demo_time: str
    status: str
    preferred_contact_method: str
    notes: Optional[str] = None
    zoom_link: Optional[str] = None
    confirmation_sent: bool
    created_at: datetime
    updated_at: datetime


class BookingListResponse(BaseModel):
    total: int
    count: int
    page: int
    page_size: int
    bookings: List[DemoBookingResponse]


class BookingStatusUpdate(BaseModel):
    status: str


class BookingStatsResponse(BaseModel):
    total_bookings: int
    scheduled: int
    confirmed: int
    completed: int
    cancelled: int
