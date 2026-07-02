from django.conf import settings


def site_settings(request):
    return {
        "SCHOOL_NAME": settings.SCHOOL_NAME,
        "EVENT_SHORT_NAME": settings.EVENT_SHORT_NAME,
        "EVENT_FULL_NAME": settings.EVENT_FULL_NAME,
        "EVENT_DATE_TEXT": settings.EVENT_DATE_TEXT,
        "EVENT_VENUE": settings.EVENT_VENUE,
        "REGISTRATION_FEE": settings.REGISTRATION_FEE,
    }
