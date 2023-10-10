from abc import ABC

from django.contrib import messages
from django.core.cache import cache
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import FormView

from .constants import (
    OTP_TOKEN_FINNOTECH_CACHE_KEY,
    SMS_AUTH_ENDPOINT_SESSION_KEY,
    BackChequeInquiry,
    FinnotechEndpoint,
    NationalcodeMobileVerification,
    PostalcodeInquiry,
)
from .forms import NationalcodeMobileForm, OTPForm, PostalCodeForm
from .mixins import FinnotechClientAuthMixin


class BaseView(FinnotechClientAuthMixin, View):
    pass


class AuthorizationBaseView(BaseView):
    def dispatch(self, request, *args, **kwargs):
        if not (endpoint := request.session.get(SMS_AUTH_ENDPOINT_SESSION_KEY, None)):
            return HttpResponseBadRequest(
                _("You don't have any on-going authorization request.")
            )

        self.finnotech_endpoint = FinnotechEndpoint.from_dict(endpoint)
        return super().dispatch(request, *args, **kwargs)

    def get_cache_key(self, mobile):
        return OTP_TOKEN_FINNOTECH_CACHE_KEY % self.cache_key_params


class RequestOTPView(FormView, AuthorizationBaseView):
    template_name = "finnotech/finnotech_form.html"
    form_class = NationalcodeMobileForm

    def form_valid(self, form):
        mobile = form.cleaned_data.get("mobile")
        nid = form.cleaned_data.get("national_id")

        cache_key = self.get_cache_key(mobile)
        if cache.has_key(cache_key):
            messages.info(self.request, _("You don't need to authorize again."))
            return redirect

        self.send_finnotech_otp(mobile)
        self.request.session.update(
            {
                "mobile": mobile,
                "national_id": nid,
            }
        )
        return redirect("finnotech:sms_auth:otp")


class OTPView(FormView, AuthorizationBaseView):
    template_name = "finnotech/finnotech_form.html"
    form_class = OTPForm

    def form_valid(self, form):
        otp = form.cleaned_data.get("otp")
        mobile = self.request.session.get("mobile")
        nid = self.request.session.get("national_id")

        self.verify_finnotech_otp(mobile, nid, otp)
        self.get_finnotech_authtoken(mobile)

        messages.success(self.request, _("Your token was successfully obtained."))
        return redirect(self.redirect_url)


class NationalcodeMobileVerificationView(FormView, BaseView):
    finnotech_endpoint = NationalcodeMobileVerification
    form_class = NationalcodeMobileForm
    template_name = "finnotech/clientauth_form.html"

    def form_valid(self, form):
        national_id = form.cleaned_data.get("national_id")
        mobile = form.cleaned_data.get("mobile")

        finnotech_response = self.make_finnotech_request(
            national_id=national_id, mobile=mobile
        )
        context = {
            "is_valid": finnotech_response.is_valid,
            "form": form,
        }
        return self.render_to_response(context)


class PostalCodeView(FormView, BaseView):
    finnotech_endpoint = PostalcodeInquiry
    form_class = PostalCodeForm
    template_name = "finnotech/finnotech_form.html"

    def form_valid(self, form):
        postal_code = form.cleaned_data.get("postal_code")

        finnotech_response = self.make_finnotech_request(postal_code=postal_code)
        context = {
            "form": form,
            "data": finnotech_response.payload,
        }
        return self.render_to_response(context)


class BackChequeInquiryView(FormView, BaseView):
    finnotech_endpoint = BackChequeInquiry
    template_name = "finnotech/finnotech_form.html"
    form_class = NationalcodeMobileForm

    def form_valid(self, form):
        mobile = form.cleaned_data.get("mobile")
        nid = form.cleaned_data.get("national_id")
        cache_key = self.get_cache_key(mobile)

        # check if user already has an sms-auth token.
        if not (token := cache.get(cache_key)):
            self.request.session[
                SMS_AUTH_ENDPOINT_SESSION_KEY
            ] = self.finnotech_endpoint.to_dict()
            messages.info(self.request, _("Please fill in the form"))
            return redirect("finnotech:sms_auth:request_otp")

        finnotech_response = self.make_finnotech_request(token=token, national_id=nid)
        context = {
            "data": finnotech_response.payload,
            "form": form,
        }
        return self.render_to_response(context)
