from django import forms
from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _
from phonenumber_field.formfields import PhoneNumberField


class NationalcodeMobileForm(forms.Form):
    national_id = forms.CharField(max_length=10, label=_("National ID"))
    mobile = PhoneNumberField(region="IR", label=_("Mobile"))

    def clean_mobile(self):
        if data := self.cleaned_data.get("mobile"):
            data = data.as_national.replace(" ", "")

        return data


class OTPForm(forms.Form):
    otp = forms.CharField(max_length=5, min_length=5, label=_("OTP"))


class PostalCodeForm(forms.Form):
    postal_code = forms.CharField(max_length=10, min_length=10, label=_("Postal Code"))
