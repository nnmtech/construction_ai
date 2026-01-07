"""Contact form endpoints."""

from __future__ import annotations

import logging
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.contractor import Contractor, ContactFormSubmission
from app.utils.email import send_welcome_email

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/forms",
    tags=["forms"],
)


class ContactFormRequest(BaseModel):
    company_name: str = Field(..., min_length=2, max_length=255)
    contact_name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    phone: str | None = Field(None, max_length=20)
    company_size: str | None = None
    annual_revenue: float | None = Field(None, ge=0)
    current_challenges: str | None = Field(None, max_length=2000)


class ContactFormResponse(BaseModel):
    contractor_id: int
    submission_id: int
    created_at: datetime


@router.post(
    "/contact",
    response_model=ContactFormResponse,
    status_code=status.HTTP_201_CREATED,
)
def submit_contact_form(
    payload: ContactFormRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> ContactFormResponse:
    # Upsert contractor by email
    contractor = db.query(Contractor).filter(Contractor.email == payload.email).one_or_none()

    if contractor is None:
        contractor = Contractor(
            company_name=payload.company_name,
            contact_name=payload.contact_name,
            email=str(payload.email),
            phone=payload.phone,
            company_size=payload.company_size,
            annual_revenue=payload.annual_revenue,
            current_challenges=payload.current_challenges,
        )
        db.add(contractor)
        db.flush()  # populate contractor.id
    else:
        # Keep existing values unless new value provided
        contractor.company_name = payload.company_name or contractor.company_name
        contractor.contact_name = payload.contact_name or contractor.contact_name
        contractor.phone = payload.phone or contractor.phone
        contractor.company_size = payload.company_size or contractor.company_size
        contractor.annual_revenue = payload.annual_revenue if payload.annual_revenue is not None else contractor.annual_revenue
        contractor.current_challenges = payload.current_challenges or contractor.current_challenges

    submission = ContactFormSubmission(
        contractor_id=contractor.id,
        company_name=payload.company_name,
        contact_name=payload.contact_name,
        email=str(payload.email),
        phone=payload.phone,
        company_size=payload.company_size,
        annual_revenue=payload.annual_revenue,
        current_challenges=payload.current_challenges,
    )
    db.add(submission)

    db.commit()
    db.refresh(submission)

    # Welcome email (optional; will no-op if not configured)
    background_tasks.add_task(send_welcome_email, str(payload.email), payload.company_name, payload.contact_name)

    return ContactFormResponse(
        contractor_id=contractor.id,
        submission_id=submission.id,
        created_at=submission.created_at,
    )
