"""Email utilities.

The application treats email as optional: if SMTP credentials are not configured,
email functions will no-op (and log).

These functions are async because the route modules call them with `await`.
"""

from __future__ import annotations

import asyncio
import logging
from email.message import EmailMessage

import aiosmtplib

from app.config import settings

logger = logging.getLogger(__name__)


def _smtp_configured() -> bool:
    user = getattr(settings, 'SMTP_USER', '')
    password = getattr(settings, 'SMTP_PASSWORD', '')
    host = getattr(settings, 'SMTP_HOST', '')
    port = getattr(settings, 'SMTP_PORT', 0)

    # Treat placeholder defaults as "not configured"
    if not user or user == 'your-email@gmail.com':
        return False
    if not password or password == 'your-app-password':
        return False
    if not host:
        return False
    if not port:
        return False

    return True


async def _send_email(to_email: str, subject: str, html_body: str) -> None:
    if not _smtp_configured():
        logger.info('Email not sent (SMTP not configured): %s -> %s', subject, to_email)
        return

    msg = EmailMessage()
    msg['From'] = f"{getattr(settings, 'SENDER_NAME', 'Construction AI')} <{getattr(settings, 'SENDER_EMAIL', settings.SMTP_USER)}>"
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.set_content('This email requires an HTML-capable client.')
    msg.add_alternative(html_body, subtype='html')

    await aiosmtplib.send(
        msg,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASSWORD,
        start_tls=getattr(settings, 'SMTP_TLS', True),
        timeout=20,
    )


async def send_demo_confirmation_email(*, contractor, booking) -> None:
    """Compatibility helper for `app_routes_booking_complete.py`.

    Expects keyword arguments: contractor, booking.
    """

    await send_booking_confirmation_email(
        email=getattr(contractor, "email", ""),
        company_name=getattr(contractor, "company_name", ""),
        contact_name=getattr(contractor, "contact_name", ""),
        booking_datetime=getattr(booking, "demo_date", None),
    )


async def send_email(email: str, subject: str, html_body: str) -> None:
    """Generic email sender used by auth flows."""
    await _send_email(email, subject, html_body)


async def send_welcome_email(email: str, company_name: str, contact_name: str) -> None:
    subject = 'Welcome to Construction AI'
    body = f"""    <h2>Hi {contact_name},</h2>
    <p>Thanks for your interest in Construction AI.</p>
    <p>We received your request from <strong>{company_name}</strong>.</p>
    <p>You can book a demo any time at <a href="/booking">/booking</a>.</p>
    """
    await _send_email(email, subject, body)


async def send_roi_report_email(email: str, company_name: str, contact_name: str, roi_data) -> None:
    subject = f'Your Construction AI ROI Report - {company_name}'
    body = f"""    <h2>ROI Report for {company_name}</h2>
    <p>Hi {contact_name},</p>
    <p>Here is your ROI report data:</p>
    <pre>{roi_data}</pre>
    """
    await _send_email(email, subject, body)


async def send_booking_confirmation_email(email: str, company_name: str, contact_name: str, booking_datetime) -> None:
    subject = 'Your Construction AI Demo is Scheduled'
    body = f"""    <h2>Demo Scheduled</h2>
    <p>Hi {contact_name},</p>
    <p>Your demo for <strong>{company_name}</strong> is scheduled for:</p>
    <p><strong>{booking_datetime}</strong></p>
    """
    await _send_email(email, subject, body)


async def send_booking_reminder_email(email: str, company_name: str, contact_name: str, booking_datetime) -> None:
    subject = 'Reminder: Upcoming Construction AI Demo'
    body = f"""    <h2>Demo Reminder</h2>
    <p>Hi {contact_name},</p>
    <p>This is a reminder for your upcoming demo:</p>
    <p><strong>{booking_datetime}</strong></p>
    """
    await _send_email(email, subject, body)
