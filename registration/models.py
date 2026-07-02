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

DRIVER_FEE = 500


def calculate_registration_fee(ssc_batch):
    """
    Fee tiers (as of the school's official notice):
      1963 - 2019  -> 1500 taka
      2020 - 2026  -> 1000 taka
      2027 onwards -> 300 taka (current students of the school, not yet passed SSC)
    """
    try:
        year = int(ssc_batch)
    except (TypeError, ValueError):
        return 1500

    if year <= 2019:
        return 1500
    elif year <= 2026:
        return 1000
    else:
        return 300


def calculate_total_fee(ssc_batch, is_driver=False):
    total = calculate_registration_fee(ssc_batch)
    if is_driver:
        total += DRIVER_FEE
    return total


class Registrant(models.Model):
    # Personal info
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, help_text="Primary mobile number (mandatory)")
    secondary_phone = models.CharField(max_length=20, blank=True, null=True)
    whatsapp_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField()
    last_class_attended = models.CharField(
        max_length=100, help_text="e.g. Class 10 / SSC / Science-A"
    )
    ssc_batch = models.PositiveIntegerField(
        help_text="SSC Batch year. If not yet passed, the year you would/will pass."
    )
    ssc_passing_year = models.PositiveIntegerField(
        blank=True, null=True, help_text="Actual SSC passing year (optional)"
    )
    blood_group = models.CharField(max_length=5, blank=True, null=True)
    present_address = models.CharField(max_length=255, blank=True, null=True)
    tshirt_size = models.CharField(max_length=4, choices=TSHIRT_CHOICES)
    is_driver = models.BooleanField(
        default=False, help_text="Bringing own driver (+৳500, lunch only)"
    )

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

    @property
    def is_current_student(self):
        return self.ssc_batch > 2026

    @property
    def fee_tier_label(self):
        if self.is_current_student:
            return "স্কুলের বর্তমান ছাত্র/ছাত্রী"
        elif self.ssc_batch <= 2019:
            return "১৯৬৩ - ২০১৯ ব্যাচ"
        else:
            return "২০২০ - ২০২৬ ব্যাচ"
