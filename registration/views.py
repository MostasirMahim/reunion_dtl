import uuid

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .forms import RegistrationForm, SpecialFundingForm, AdminLoginForm, RegistrantSearchForm
from .models import Registrant, SpecialFunding, calculate_total_fee
from .sslcommerz import init_payment, init_funding_payment, validate_payment
from .ticket_utils import generate_qr_code, generate_ticket_pdf
from .email_utils import send_ticket_email, send_payment_receipt_email


# ---------------------------------------------------------------------------
# PUBLIC PAGES
# ---------------------------------------------------------------------------
def home(request):
    return render(request, "registration/home.html")


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            registrant = form.save(commit=False)
            registrant.amount = calculate_total_fee(registrant.ssc_batch)
            registrant.transaction_id = f"BSSR-{uuid.uuid4().hex[:16].upper()}"
            registrant.save()

            request.session["pending_registrant_id"] = registrant.id

            try:
                ssl_response = init_payment(registrant, request)
            except Exception:
                ssl_response = {}

            gateway_url = ssl_response.get("GatewayPageURL")
            if gateway_url:
                return redirect(gateway_url)
            else:
                messages.error(
                    request,
                    "Could not connect to the payment gateway. Please try again in a moment."
                )
                registrant.delete()
    else:
        form = RegistrationForm()

    return render(request, "registration/register.html", {"form": form})


def special_funding(request):
    if request.method == "POST":
        form = SpecialFundingForm(request.POST)
        if form.is_valid():
            funding = form.save(commit=False)
            funding.transaction_id = f"BSSF-{uuid.uuid4().hex[:16].upper()}"
            funding.save()

            try:
                ssl_response = init_funding_payment(funding, request)
            except Exception:
                ssl_response = {}

            gateway_url = ssl_response.get("GatewayPageURL")
            if gateway_url:
                return redirect(gateway_url)
            else:
                messages.error(
                    request,
                    "Could not connect to the payment gateway. Please try again in a moment."
                )
                funding.delete()
    else:
        form = SpecialFundingForm(initial={"funding_type": "individual"})

    return render(request, "registration/special_funding.html", {"form": form})


@csrf_exempt
def payment_success(request):
    tran_id = request.POST.get("tran_id") or request.GET.get("tran_id")
    val_id = request.POST.get("val_id") or request.GET.get("val_id")

    if tran_id and tran_id.startswith("BSSF-"):
        funding = get_object_or_404(SpecialFunding, transaction_id=tran_id)
        _finalize_funding_payment(funding, val_id)
        return redirect(reverse("registration:funding_success", args=[funding.funding_id]))

    registrant = get_object_or_404(Registrant, transaction_id=tran_id)
    _finalize_payment(registrant, val_id)
    return redirect(reverse("registration:ticket_view", args=[registrant.registration_id, registrant.verify_token]))


@csrf_exempt
def payment_fail(request):
    tran_id = request.POST.get("tran_id") or request.GET.get("tran_id")

    if tran_id and tran_id.startswith("BSSF-"):
        funding = SpecialFunding.objects.filter(transaction_id=tran_id).first()
        if funding and funding.payment_status == "pending":
            funding.payment_status = "failed"
            funding.save(update_fields=["payment_status"])
        return render(request, "registration/payment_result.html", {
            "status": "failed", "funding": funding,
        })

    registrant = Registrant.objects.filter(transaction_id=tran_id).first()
    if registrant and registrant.payment_status == "pending":
        registrant.payment_status = "failed"
        registrant.save(update_fields=["payment_status"])
    return render(request, "registration/payment_result.html", {
        "status": "failed", "registrant": registrant,
    })


@csrf_exempt
def payment_cancel(request):
    tran_id = request.POST.get("tran_id") or request.GET.get("tran_id")

    if tran_id and tran_id.startswith("BSSF-"):
        funding = SpecialFunding.objects.filter(transaction_id=tran_id).first()
        if funding and funding.payment_status == "pending":
            funding.payment_status = "cancelled"
            funding.save(update_fields=["payment_status"])
        return render(request, "registration/payment_result.html", {
            "status": "cancelled", "funding": funding,
        })

    registrant = Registrant.objects.filter(transaction_id=tran_id).first()
    if registrant and registrant.payment_status == "pending":
        registrant.payment_status = "cancelled"
        registrant.save(update_fields=["payment_status"])
    return render(request, "registration/payment_result.html", {
        "status": "cancelled", "registrant": registrant,
    })


@csrf_exempt
def payment_ipn(request):
    """SSLCommerz server-to-server Instant Payment Notification."""
    tran_id = request.POST.get("tran_id")
    val_id = request.POST.get("val_id")

    if tran_id and tran_id.startswith("BSSF-"):
        funding = SpecialFunding.objects.filter(transaction_id=tran_id).first()
        if funding and funding.payment_status != "paid":
            _finalize_funding_payment(funding, val_id)
        return render(request, "registration/ipn_ack.html")

    registrant = Registrant.objects.filter(transaction_id=tran_id).first()
    if registrant and registrant.payment_status != "paid":
        _finalize_payment(registrant, val_id)
    return render(request, "registration/ipn_ack.html")


def _finalize_payment(registrant, val_id):
    if registrant.payment_status == "paid":
        return
    try:
        result = validate_payment(val_id)
    except Exception:
        result = {}

    if result.get("status") in ("VALID", "VALIDATED"):
        registrant.payment_status = "paid"
        registrant.sslcz_val_id = val_id
        registrant.sslcz_bank_tran_id = result.get("bank_tran_id", "")
        registrant.sslcz_card_type = result.get("card_type", "")
        registrant.paid_at = timezone.now()
        registrant.save()

        generate_qr_code(registrant)
        generate_ticket_pdf(registrant)
        registrant.save()

        try:
            send_ticket_email(registrant)
        except Exception:
            pass
        try:
            send_payment_receipt_email(registrant)
        except Exception:
            pass


def _finalize_funding_payment(funding, val_id):
    if funding.payment_status == "paid":
        return
    try:
        result = validate_payment(val_id)
    except Exception:
        result = {}

    if result.get("status") in ("VALID", "VALIDATED"):
        funding.payment_status = "paid"
        funding.sslcz_val_id = val_id
        funding.sslcz_bank_tran_id = result.get("bank_tran_id", "")
        funding.sslcz_card_type = result.get("card_type", "")
        funding.paid_at = timezone.now()
        funding.save()


def funding_success(request, funding_id):
    funding = get_object_or_404(SpecialFunding, funding_id=funding_id)
    return render(request, "registration/funding_success.html", {"funding": funding})


def ticket_view(request, registration_id, token):
    registrant = get_object_or_404(
        Registrant, registration_id=registration_id, verify_token=token
    )
    return render(request, "registration/ticket_view.html", {"registrant": registrant})


def verify_ticket(request, registration_id, token):
    """Page opened when QR code is scanned at the gate."""
    registrant = Registrant.objects.filter(
        registration_id=registration_id, verify_token=token
    ).first()

    if not registrant:
        return render(request, "registration/verify.html", {"valid": False})

    if request.method == "POST" and request.POST.get("action") == "checkin":
        if request.user.is_authenticated:
            registrant.is_checked_in = True
            registrant.checked_in_at = timezone.now()
            registrant.save(update_fields=["is_checked_in", "checked_in_at"])
            messages.success(request, "Checked-in successfully!")

    return render(request, "registration/verify.html", {
        "valid": True, "registrant": registrant,
    })


# ---------------------------------------------------------------------------
# ADMIN PANEL (custom, separate from /django-admin/)
# ---------------------------------------------------------------------------
def admin_login(request):
    if request.user.is_authenticated:
        return redirect("registration:admin_dashboard")

    form = AdminLoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password"],
        )
        if user is not None and user.is_staff:
            login(request, user)
            return redirect("registration:admin_dashboard")
        messages.error(request, "Incorrect username/password or no staff access.")

    return render(request, "registration/admin_panel/login.html", {"form": form})


@login_required(login_url="registration:admin_login")
def admin_logout(request):
    logout(request)
    return redirect("registration:admin_login")


def _filtered_registrants(request):
    """Apply the dashboard's search / status / batch filters to the queryset.

    Shared by the dashboard and the Excel export so that whatever is on screen
    is exactly what gets downloaded.
    """
    qs = Registrant.objects.all()
    search_form = RegistrantSearchForm(request.GET or None)
    applied = []

    if search_form.is_valid():
        q = (search_form.cleaned_data.get("q") or "").strip()
        status = search_form.cleaned_data.get("status")
        ssc_batch = search_form.cleaned_data.get("ssc_batch")

        if q:
            qs = qs.filter(
                Q(full_name__icontains=q)
                | Q(phone__icontains=q)
                | Q(email__icontains=q)
                | Q(registration_id__icontains=q)
                | Q(transaction_id__icontains=q)
            )
            applied.append(f'Search: "{q}"')
        if status:
            qs = qs.filter(payment_status=status)
            applied.append(f"Status: {status.title()}")
        if ssc_batch:
            qs = qs.filter(ssc_batch=ssc_batch)
            applied.append(f"SSC Batch: {ssc_batch}")

    return qs, search_form, applied


@login_required(login_url="registration:admin_login")
def admin_export_registrants(request):
    """Download the currently filtered registrant list as a styled .xlsx file."""
    try:
        from .export_utils import build_registrants_workbook
    except ImportError:
        messages.error(
            request,
            "Excel export needs the 'openpyxl' package. "
            "Install it with: pip install openpyxl",
        )
        return redirect("registration:admin_dashboard")

    qs, _form, applied = _filtered_registrants(request)
    qs = qs.order_by("-created_at")

    summary = " | ".join(applied) if applied else "All registrations"
    workbook = build_registrants_workbook(qs, filter_summary=summary)

    stamp = timezone.localtime(timezone.now()).strftime("%Y%m%d-%H%M")
    slug = "filtered" if applied else "all"
    filename = f"bss-reunion-registrations-{slug}-{stamp}.xlsx"

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    workbook.save(response)
    return response


@login_required(login_url="registration:admin_login")
def admin_dashboard(request):
    qs, search_form, applied_filters = _filtered_registrants(request)

    total_registrants = Registrant.objects.count()
    total_paid = Registrant.objects.filter(payment_status="paid").count()
    total_checked_in = Registrant.objects.filter(is_checked_in=True).count()
    total_revenue = sum(
        r.amount for r in Registrant.objects.filter(payment_status="paid")
    )
    total_funding = sum(
        f.amount for f in SpecialFunding.objects.filter(payment_status="paid")
    )

    paginator = Paginator(qs.order_by("-created_at"), 20)
    page_obj = paginator.get_page(request.GET.get("page"))

    # Keep the active filters in the pagination + export links.
    params = request.GET.copy()
    params.pop("page", None)
    querystring = params.urlencode()

    return render(request, "registration/admin_panel/dashboard.html", {
        "search_form": search_form,
        "page_obj": page_obj,
        "paginator": paginator,
        "applied_filters": applied_filters,
        "querystring": querystring,
        "filtered_count": paginator.count,
        "total_registrants": total_registrants,
        "total_paid": total_paid,
        "total_checked_in": total_checked_in,
        "total_revenue": total_revenue,
        "total_funding": total_funding,
    })


@login_required(login_url="registration:admin_login")
def admin_registrant_detail(request, pk):
    registrant = get_object_or_404(Registrant, pk=pk)
    return render(request, "registration/admin_panel/detail.html", {
        "registrant": registrant,
    })


@login_required(login_url="registration:admin_login")
@require_POST
def admin_toggle_checkin(request, pk):
    registrant = get_object_or_404(Registrant, pk=pk)
    registrant.is_checked_in = not registrant.is_checked_in
    registrant.checked_in_at = timezone.now() if registrant.is_checked_in else None
    registrant.save(update_fields=["is_checked_in", "checked_in_at"])
    messages.success(request, "Check-in status updated.")
    return redirect("registration:admin_registrant_detail", pk=pk)


def public_status_check(request):
    """Public page: anyone can check their registration status by
    Registration ID or Phone Number (no login needed)."""
    query = request.GET.get("q", "").strip()
    results = []
    searched = False

    if query:
        searched = True
        results = Registrant.objects.filter(
            Q(registration_id__iexact=query) | Q(phone__icontains=query)
        )[:10]

    return render(request, "registration/status_check.html", {
        "query": query, "results": results, "searched": searched,
    })
