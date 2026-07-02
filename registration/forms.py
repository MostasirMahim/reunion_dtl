from django import forms
from .models import Registrant


class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Registrant
        fields = [
            "full_name",
            "phone",
            "email",
            "passing_year",
            "department_class",
            "blood_group",
            "present_address",
            "tshirt_size",
        ]
        widgets = {
            "full_name": forms.TextInput(attrs={
                "class": "form-input", "placeholder": "আপনার পূর্ণ নাম লিখুন"
            }),
            "phone": forms.TextInput(attrs={
                "class": "form-input", "placeholder": "01XXXXXXXXX"
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-input", "placeholder": "you@example.com"
            }),
            "passing_year": forms.NumberInput(attrs={
                "class": "form-input", "placeholder": "e.g. 2005", "min": 1960, "max": 2030
            }),
            "department_class": forms.TextInput(attrs={
                "class": "form-input", "placeholder": "e.g. Science / Commerce / Arts"
            }),
            "blood_group": forms.TextInput(attrs={
                "class": "form-input", "placeholder": "e.g. B+ (optional)"
            }),
            "present_address": forms.TextInput(attrs={
                "class": "form-input", "placeholder": "Present address (optional)"
            }),
            "tshirt_size": forms.Select(attrs={"class": "form-select"}),
        }

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        digits = phone.replace("+", "").replace(" ", "").replace("-", "")
        if not digits.isdigit() or len(digits) < 10:
            raise forms.ValidationError("সঠিক মোবাইল নম্বর দিন।")
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
