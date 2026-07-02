import random
import string
import uuid

from django.conf import settings
from django.db import models


def generate_registration_id():
    """e.g. BSSR26-000123 style unique id based on event short name."""
    prefix = getattr(settings, "EVENT_SHORT_NAME", "BSSREUNION")[:4].upper()
    year_part = "26"
    rand_part = "".join(random.choices(string.digits, k=6))
    return f"{prefix}{year_part}-{rand_part}"


TSHIRT_CHOICES = [
    ("S", "Small"),
    ("M", "Medium"),
    ("L", "Large"),
    ("XL", "X-Large"),
    ("XXL", "XX-Large"),
]

PAYMENT_STATUS_CHOICES = [
    ("pending", "Pending"),
    ("paid", "Paid"),
    ("failed", "Failed"),
    ("cancelled", "Cancelled"),
]


class Registrant(models.Model):
    # Personal info
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    passing_year = models.PositiveIntegerField(help_text="SSC / Passing Year")
    department_class = models.CharField(
        max_length=100, help_text="e.g. Science / Commerce / Class 10-A"
    )
    blood_group = models.CharField(max_length=5, blank=True, null=True)
    present_address = models.CharField(max_length=255, blank=True, null=True)
    tshirt_size = models.CharField(max_length=4, choices=TSHIRT_CHOICES)

    # Registration meta
    registration_id = models.CharField(
        max_length=30, unique=True, default=generate_registration_id, editable=False
    )
    verify_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    # Payment
    amount = models.PositiveIntegerField(default=0)
    payment_status = models.CharField(
        max_length=10, choices=PAYMENT_STATUS_CHOICES, default="pending"
    )
    transaction_id = models.CharField(max_length=64, unique=True)
    sslcz_val_id = models.CharField(max_length=100, blank=True, null=True)
    sslcz_bank_tran_id = models.CharField(max_length=100, blank=True, null=True)
    sslcz_card_type = models.CharField(max_length=50, blank=True, null=True)
    paid_at = models.DateTimeField(blank=True, null=True)

    # Ticket
    qr_code = models.ImageField(upload_to="qrcodes/", blank=True, null=True)
    ticket_pdf = models.FileField(upload_to="tickets/", blank=True, null=True)
    ticket_emailed = models.BooleanField(default=False)
    receipt_emailed = models.BooleanField(default=False)

    # Entry / check-in
    is_checked_in = models.BooleanField(default=False)
    checked_in_at = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} ({self.registration_id})"

    @property
    def is_paid(self):
        return self.payment_status == "paid"
