from django.urls import path
from . import views

app_name = "registration"

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("special-funding/", views.special_funding, name="special_funding"),
    path("special-funding/thank-you/<str:funding_id>/", views.funding_success, name="funding_success"),

    path("payment/success/", views.payment_success, name="payment_success"),
    path("payment/fail/", views.payment_fail, name="payment_fail"),
    path("payment/cancel/", views.payment_cancel, name="payment_cancel"),
    path("payment/ipn/", views.payment_ipn, name="payment_ipn"),

    path("ticket/<str:registration_id>/<uuid:token>/", views.ticket_view, name="ticket_view"),
    path("verify/<str:registration_id>/<uuid:token>/", views.verify_ticket, name="verify_ticket"),
    path("check-status/", views.public_status_check, name="public_status_check"),

    path("admin-panel/login/", views.admin_login, name="admin_login"),
    path("admin-panel/logout/", views.admin_logout, name="admin_logout"),
    path("admin-panel/dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin-panel/registrant/<int:pk>/", views.admin_registrant_detail, name="admin_registrant_detail"),
    path("admin-panel/registrant/<int:pk>/toggle-checkin/", views.admin_toggle_checkin, name="admin_toggle_checkin"),
]