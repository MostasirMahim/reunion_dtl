from django.contrib import admin
from .models import Registrant, SpecialFunding


@admin.register(Registrant)
class RegistrantAdmin(admin.ModelAdmin):
    list_display = (
        "registration_id", "full_name", "phone", "email",
        "ssc_batch", "amount", "payment_status", "is_checked_in", "created_at",
    )
    list_filter = ("payment_status", "is_checked_in", "tshirt_size", "ssc_batch")
    search_fields = ("full_name", "phone", "secondary_phone", "whatsapp_number", "email", "registration_id", "transaction_id")
    readonly_fields = (
        "registration_id", "verify_token", "transaction_id",
        "qr_code", "ticket_pdf", "created_at", "updated_at",
    )


@admin.register(SpecialFunding)
class SpecialFundingAdmin(admin.ModelAdmin):
    list_display = (
        "funding_id", "funding_type", "display_name", "amount",
        "payment_status", "created_at",
    )
    list_filter = ("payment_status", "funding_type")
    search_fields = ("funding_id", "contributor_name", "contributor_phone", "transaction_id")
    readonly_fields = ("funding_id", "transaction_id", "created_at", "updated_at")
