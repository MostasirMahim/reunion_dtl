"""
Minimal SSLCommerz integration (no third-party SDK needed).
Docs: https://developer.sslcommerz.com/
"""
import requests
from django.conf import settings

SANDBOX_INIT_URL = "https://sandbox.sslcommerz.com/gwprocess/v4/api.php"
LIVE_INIT_URL = "https://securepay.sslcommerz.com/gwprocess/v4/api.php"

SANDBOX_VALIDATION_URL = "https://sandbox.sslcommerz.com/validator/api/validationserverAPI.php"
LIVE_VALIDATION_URL = "https://securepay.sslcommerz.com/validator/api/validationserverAPI.php"


def _init_url():
    return SANDBOX_INIT_URL if settings.SSLCOMMERZ_IS_SANDBOX else LIVE_INIT_URL


def _validation_url():
    return SANDBOX_VALIDATION_URL if settings.SSLCOMMERZ_IS_SANDBOX else LIVE_VALIDATION_URL


def init_payment(registrant, request):
    """
    Calls SSLCommerz session API and returns the GatewayPageURL
    that the user should be redirected to for completing payment.
    """
    base_url = settings.SITE_BASE_URL.rstrip("/")

    payload = {
        "store_id": settings.SSLCOMMERZ_STORE_ID,
        "store_passwd": settings.SSLCOMMERZ_STORE_PASSWORD,
        "total_amount": registrant.amount,
        "currency": "BDT",
        "tran_id": registrant.transaction_id,
        "success_url": f"{base_url}/payment/success/",
        "fail_url": f"{base_url}/payment/fail/",
        "cancel_url": f"{base_url}/payment/cancel/",
        "ipn_url": f"{base_url}/payment/ipn/",
        "cus_name": registrant.full_name,
        "cus_email": registrant.email,
        "cus_add1": registrant.present_address or "N/A",
        "cus_city": "Dhaka",
        "cus_country": "Bangladesh",
        "cus_phone": registrant.phone,
        "shipping_method": "NO",
        "product_name": f"{settings.EVENT_SHORT_NAME} Registration",
        "product_category": "Event Registration",
        "product_profile": "general",
        "value_a": registrant.registration_id,  # custom value to identify on callback
    }

    response = requests.post(_init_url(), data=payload, timeout=20)
    data = response.json()
    return data


def validate_payment(val_id):
    """Server-to-server validation of a transaction using val_id."""
    params = {
        "val_id": val_id,
        "store_id": settings.SSLCOMMERZ_STORE_ID,
        "store_passwd": settings.SSLCOMMERZ_STORE_PASSWORD,
        "format": "json",
    }
    response = requests.get(_validation_url(), params=params, timeout=20)
    return response.json()
