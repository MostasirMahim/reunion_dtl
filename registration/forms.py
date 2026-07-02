from django import forms
from .models import Registrant


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
            "is_driver",
        ]
        widgets = {
            "full_name": forms.TextInput(attrs={
                "class": "form-input", "placeholder": "আপনার পূর্ণ নাম লিখুন"
            }),
            "phone": forms.TextInput(attrs={
                "class": "form-input", "placeholder": "01XXXXXXXXX"
            }),
            "secondary_phone": forms.TextInput(attrs={
                "class": "form-input", "placeholder": "01XXXXXXXXX (ঐচ্ছিক)"
            }),
            "whatsapp_number": forms.TextInput(attrs={
                "class": "form-input", "placeholder": "WhatsApp নম্বর (ঐচ্ছিক)"
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-input", "placeholder": "you@example.com"
            }),
            "last_class_attended": forms.TextInput(attrs={
                "class": "form-input", "placeholder": "e.g. Class 10 / SSC / Science-A"
            }),
            "ssc_batch": forms.NumberInput(attrs={
                "class": "form-input", "placeholder": "e.g. 2005", "min": 1963, "max": 2035
            }),
            "ssc_passing_year": forms.NumberInput(attrs={
                "class": "form-input", "placeholder": "e.g. 2005 (ঐচ্ছিক)", "min": 1963, "max": 2035
            }),
            "blood_group": forms.TextInput(attrs={
                "class": "form-input", "placeholder": "e.g. B+ (optional)"
            }),
            "present_address": forms.TextInput(attrs={
                "class": "form-input", "placeholder": "Present address (optional)"
            }),
            "tshirt_size": forms.Select(attrs={"class": "form-select"}),
            "is_driver": forms.CheckboxInput(attrs={"class": "form-checkbox"}),
        }

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        digits = phone.replace("+", "").replace(" ", "").replace("-", "")
        if not digits.isdigit() or len(digits) < 10:
            raise forms.ValidationError("সঠিক মোবাইল নম্বর দিন।")
        return phone

    def clean_secondary_phone(self):
        phone = (self.cleaned_data.get("secondary_phone") or "").strip()
        if not phone:
            return phone
        digits = phone.replace("+", "").replace(" ", "").replace("-", "")
        if not digits.isdigit() or len(digits) < 10:
            raise forms.ValidationError("সঠিক মোবাইল নম্বর দিন।")
        return phone

    def clean_whatsapp_number(self):
        phone = (self.cleaned_data.get("whatsapp_number") or "").strip()
        if not phone:
            return phone
        digits = phone.replace("+", "").replace(" ", "").replace("-", "")
        if not digits.isdigit() or len(digits) < 10:
            raise forms.ValidationError("সঠিক WhatsApp নম্বর দিন।")
        return phone


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
            "placeholder": "নাম, ফোন নম্বর বা রেজিস্ট্রেশন আইডি দিয়ে খুঁজুন...",
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
