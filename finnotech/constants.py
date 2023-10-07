from abc import ABC, abstractproperty

from .pyfinnotech.api import FinnotechApiClient
from .pyfinnotech.const import (
    SCOPE_BOOMRANG_SMS_SEND_EXECUTE,
    SCOPE_BOOMRANG_SMS_VERIFY_EXECUTE,
    SCOPE_BOOMRANG_TOKEN_DELETE,
    SCOPE_BOOMRANG_TOKENS_GET,
    SCOPE_BOOMRANG_WAGES_GET,
    SCOPE_CREDIT_SMS_BACK_CHEQUES_GET,
    SCOPE_CREDIT_SMS_FACILITY_INQUIRY_GET,
    SCOPE_ECITY_CC_POSTAL_CODE_INQUIRY,
    SCOPE_FACILITY_SHAHKAR_GET,
)

OTP_SEND_FINNOTECH_CACHE_KEY = "%(mobile)s_%(scope)s_sms"
OTP_VERIFY_FINNOTECH_CACHE_KEY = "%(mobile)s_%(scope)s_verify"
OTP_TOKEN_FINNOTECH_CACHE_KEY = "%(mobile)s_%(scope)s_token"
SESSIN_START_FINNOTECH_CACHE_KEY = "%(mobile)s_%(scope)s_session_start"
SMS_AUTH_ENDPOINT_SESSION_KEY = "sms_auth_endpoint"


class FinnotechEndpoint:
    scope = None
    method_name = None
    url_name = None

    @classmethod
    def to_dict(cls):
        return {
            "scope": cls.scope,
            "url_name": cls.url_name,
            "method_name": cls.method_name,
        }

    @classmethod
    def from_dict(cls, dict_):
        if not all(i in dict_ for i in ("scope", "method_name")):
            print(dict_)
            raise TypeError("Invalid dict was passed.")

        for k, v in dict_.items():
            setattr(cls, k, v)
        return cls


class NationalcodeMobileVerification(FinnotechEndpoint):
    scope = SCOPE_FACILITY_SHAHKAR_GET
    method_name = FinnotechApiClient.national_code_mobile_verification.__name__


class PostalcodeInquiry(FinnotechEndpoint):
    scope = SCOPE_ECITY_CC_POSTAL_CODE_INQUIRY
    method_name = FinnotechApiClient.postal_code_inquiry.__name__


class BackChequeInquiry(FinnotechEndpoint):
    scope = SCOPE_CREDIT_SMS_BACK_CHEQUES_GET
    method_name = FinnotechApiClient.back_cheques_inquiry.__name__
    url_name = "finnotech:back-cheques"
