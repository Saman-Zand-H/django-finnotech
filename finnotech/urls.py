from django.urls import include, path

from . import views

app_name = "finnotech"

sms_auth_urlpatterns = [
    path("request-otp/", view=views.RequestOTPView.as_view(), name="request_otp"),
    path("otp/", view=views.OTPView.as_view(), name="otp"),
]

urlpatterns = [
    path(
        route="nationalcode-mobile-verification/",
        view=views.NationalcodeMobileVerificationView.as_view(),
        name="nationalcode_mobile_verification",
    ),
    path(
        route="back-cheques",
        view=views.BackChequeInquiryView.as_view(),
        name="back-cheques",
    ),
    path(
        route="postal-code",
        view=views.PostalCodeView.as_view(),
        name="postal-code",
    ),
    path(route="sms-auth/", view=include((sms_auth_urlpatterns, "sms_auth"))),
]
