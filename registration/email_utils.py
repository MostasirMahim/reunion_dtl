from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string


def _email_ctx(registrant):
    return {
        "registrant": registrant,
        "SCHOOL_NAME": settings.SCHOOL_NAME,
        "EVENT_SHORT_NAME": settings.EVENT_SHORT_NAME,
        "EVENT_FULL_NAME": settings.EVENT_FULL_NAME,
    }


def send_ticket_email(registrant):
    """Sends the entry ticket PDF (with QR) to the registrant's email."""
    subject = f"Your Entry Ticket – {settings.EVENT_FULL_NAME}"
    html_body = render_to_string("registration/email/ticket_email.html", _email_ctx(registrant))
    msg = EmailMessage(
        subject=subject,
        body=html_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[registrant.email],
    )
    msg.content_subtype = "html"
    if registrant.ticket_pdf:
        msg.attach(
            f"ticket-{registrant.registration_id}.pdf",
            registrant.ticket_pdf.read(),
            "application/pdf",
        )
    msg.send(fail_silently=False)
    registrant.ticket_emailed = True
    registrant.save(update_fields=["ticket_emailed"])


def send_payment_receipt_email(registrant):
    """Sends an SSLCommerz payment receipt/confirmation email."""
    subject = f"Payment Receipt – {settings.EVENT_SHORT_NAME} Registration"
    html_body = render_to_string("registration/email/receipt_email.html", _email_ctx(registrant))
    msg = EmailMessage(
        subject=subject,
        body=html_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[registrant.email],
    )
    msg.content_subtype = "html"
    msg.send(fail_silently=False)
    registrant.receipt_emailed = True
    registrant.save(update_fields=["receipt_emailed"])
