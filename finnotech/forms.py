from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Field, Layout, Row, Submit
from phonenumber_field.formfields import PhoneNumberField

from django import forms
from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class NationalcodeMobileForm(forms.Form):
    national_id = forms.CharField(max_length=10, label=_("National ID"))
    mobile = PhoneNumberField(region="IR", label=_("Mobile"))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Field("national_id", wrapper_class="col-md-6"),
                Field("mobile", wrapper_class="col-md-6"),
            ),
            Submit("validate", _("Validate"), css_class="btn btn-facebook w-100"),
        )

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data["mobile"] = cleaned_data["mobile"].as_national.replace(" ", "")
        return cleaned_data


class OTPForm(forms.Form):
    otp = forms.CharField(max_length=5, min_length=5, label=_("OTP"))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(Field("otp", wrapper_class="w-100")),
            Submit("submit", _("Submit"), css_class="btn btn-success w-100"),
        )


class PostalCodeForm(forms.Form):
    postal_code = forms.CharField(max_length=10, min_length=10, label=_("Postal Code"))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(Field("postal_code", wrapper_class="w-100")),
            Submit("submit", _("Submit"), css_class="btn btn-success w-100"),
        )
