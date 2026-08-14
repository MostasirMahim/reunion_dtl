from django import forms
from .models import Registrant, SpecialFunding


# ---------------------------------------------------------------------------
# SSC year dropdown (searchable select on the front-end)
# ---------------------------------------------------------------------------
SSC_YEAR_MIN = 1963
SSC_YEAR_MAX = 2032

YEAR_RANGE = list(range(SSC_YEAR_MIN, SSC_YEAR_MAX + 1))

YEAR_CHOICES = [("", "Select year")] + [(y, str(y)) for y in YEAR_RANGE]
YEAR_CHOICES_OPTIONAL = [("", "Select year (optional)")] + [(y, str(y)) for y in YEAR_RANGE]


def _validate_year(value):
    """Guard the year range server-side (a <select> alone can be bypassed)."""
    if value in (None, ""):
        return value
    try:
        year = int(value)
    except (TypeError, ValueError):
        raise forms.ValidationError("Please select a valid year.")
    if year < SSC_YEAR_MIN or year > SSC_YEAR_MAX:
        raise forms.ValidationError(
            "Please select a year between %d and %d." % (SSC_YEAR_MIN, SSC_YEAR_MAX)
        )
    return year


def year_select(choices, placeholder):
    """A native <select> that JS upgrades into a type-to-search combobox."""
    return forms.Select(
        choices=choices,
        attrs={
            "class": "form-select searchable-select",
            "data-searchable": "true",
            "data-placeholder": placeholder,
        },
    )


class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Registrant
        fields = [
            "full_name",
            "phone",
            "secondary_phone",
            "whatsapp_number",
            "email",
            "last_class_attended",
            "ssc_batch",
            "ssc_passing_year",
            "blood_group",
            "present_address",
            "tshirt_size",
        ]
        widgets = {
            "full_name": forms.TextInput(attrs={
                "class": "form-input", "placeholder": "Enter your full name"
            }),
            "phone": forms.TextInput(attrs={
                "class": "form-input", "placeholder": "01XXXXXXXXX"
            }),
            "secondary_phone": forms.TextInput(attrs={
                "class": "form-input", "placeholder": "01XXXXXXXXX (optional)"
            }),
            "whatsapp_number": forms.TextInput(attrs={
                "class": "form-input", "placeholder": "WhatsApp number (optional)"
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-input", "placeholder": "you@example.com"
            }),
            "last_class_attended": forms.TextInput(attrs={
                "class": "form-input", "placeholder": "e.g. Class 10 / SSC / Science-A"
            }),
            "ssc_batch": year_select(
                YEAR_CHOICES, "Type or select a year — e.g. 2005"
            ),
            "ssc_passing_year": year_select(
                YEAR_CHOICES_OPTIONAL, "Type or select a year (optional)"
            ),
            "blood_group": forms.TextInput(attrs={
                "class": "form-input", "placeholder": "e.g. B+ (optional)"
            }),
            "present_address": forms.TextInput(attrs={
                "class": "form-input", "placeholder": "Present address (optional)"
            }),
            "tshirt_size": forms.Select(attrs={"class": "form-select"}),
        }

    def clean_ssc_batch(self):
        return _validate_year(self.cleaned_data.get("ssc_batch"))

    def clean_ssc_passing_year(self):
        return _validate_year(self.cleaned_data.get("ssc_passing_year"))

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        digits = phone.replace("+", "").replace(" ", "").replace("-", "")
        if not digits.isdigit() or len(digits) < 10:
            raise forms.ValidationError("Please enter a valid mobile number.")
        return phone

    def clean_secondary_phone(self):
        phone = (self.cleaned_data.get("secondary_phone") or "").strip()
        if not phone:
            return phone
        digits = phone.replace("+", "").replace(" ", "").replace("-", "")
        if not digits.isdigit() or len(digits) < 10:
            raise forms.ValidationError("Please enter a valid mobile number.")
        return phone

    def clean_whatsapp_number(self):
        phone = (self.cleaned_data.get("whatsapp_number") or "").strip()
        if not phone:
            return phone
        digits = phone.replace("+", "").replace(" ", "").replace("-", "")
        if not digits.isdigit() or len(digits) < 10:
            raise forms.ValidationError("Please enter a valid WhatsApp number.")
        return phone


class SpecialFundingForm(forms.ModelForm):
    class Meta:
        model = SpecialFunding
        fields = [
            "funding_type",
            "ssc_batch",
            "contributor_name",
            "contributor_phone",
            "amount",
        ]
        widgets = {
            "funding_type": forms.RadioSelect(attrs={"class": "form-radio"}),
            "ssc_batch": year_select(
                YEAR_CHOICES_OPTIONAL, "Type or select a year — e.g. 2005"
            ),
            "contributor_name": forms.TextInput(attrs={
                "class": "form-input", "placeholder": "Full name"
            }),
            "contributor_phone": forms.TextInput(attrs={
                "class": "form-input", "placeholder": "01XXXXXXXXX"
            }),
            "amount": forms.NumberInput(attrs={
                "class": "form-input", "placeholder": "e.g. 5000", "min": 1
            }),
        }

    def clean_ssc_batch(self):
        return _validate_year(self.cleaned_data.get("ssc_batch"))

    def clean(self):
        cleaned_data = super().clean()
        funding_type = cleaned_data.get("funding_type")

        if funding_type == "batch":
            if not cleaned_data.get("ssc_batch"):
                self.add_error("ssc_batch", "Please enter the SSC batch year.")
        elif funding_type == "individual":
            if not cleaned_data.get("contributor_name"):
                self.add_error("contributor_name", "Please enter your name.")
            if not cleaned_data.get("contributor_phone"):
                self.add_error("contributor_phone", "Please enter your phone number.")

        amount = cleaned_data.get("amount")
        if amount is not None and amount <= 0:
            self.add_error("amount", "Amount must be greater than 0.")

        return cleaned_data


class AdminLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={
        "class": "form-input", "placeholder": "Username", "autofocus": True
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        "class": "form-input", "placeholder": "Password"
    }))


class RegistrantSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-input",
            "placeholder": "Search by name, phone, or Registration ID...",
        }),
    )
    status = forms.ChoiceField(
        required=False,
        choices=[("", "All Status")] + [
            ("paid", "Paid"), ("pending", "Pending"),
            ("failed", "Failed"), ("cancelled", "Cancelled"),
        ],
        widget=forms.Select(attrs={"class": "form-select"}),
    )
