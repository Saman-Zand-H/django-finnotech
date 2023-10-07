from logging import getLogger
from operator import methodcaller

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .constants import (
    OTP_SEND_FINNOTECH_CACHE_KEY,
    OTP_TOKEN_FINNOTECH_CACHE_KEY,
    OTP_VERIFY_FINNOTECH_CACHE_KEY,
    SESSIN_START_FINNOTECH_CACHE_KEY,
    FinnotechEndpoint,
)
from .decorators import check_finnotech_timeout, handle_finnotech_error
from .pyfinnotech.api import FinnotechApiClient
from .pyfinnotech.token import SmsAuthorization

logger = getLogger(__name__)


class FinnotechClientAuthMixin:
    finnotech_endpoint: FinnotechEndpoint = None

    def dispatch(self, request, *args, **kwargs):
        self.FINNOTECH_CLIENTID = settings.FINNOTECH_CLIENTID
        self.FINNOTECH_USERNAME = settings.FINNOTECH_USERNAME
        self.FINNOTECH_PASSWORD = settings.FINNOTECH_PASSWORD
        self.FINNOTECH_REDIRECT_URL = settings.FINNOTECH_REDIRECT_URL

        self.finnotech_endpoint = self.get_finnotech_endpoint()
        self.scope = self.finnotech_endpoint.scope
        self.finnotech_apiclient = FinnotechApiClient(
            client_id=self.FINNOTECH_CLIENTID,
            client_national_id=self.FINNOTECH_USERNAME,
            client_secret=self.FINNOTECH_PASSWORD,
            scopes=[self.finnotech_endpoint.scope],
        )
        self.finnotech_sms_auth = SmsAuthorization
        self.cache_key_params = lambda i: {"scope": self.scope, "mobile": i}
        return super().dispatch(request, *args, **kwargs)

    @handle_finnotech_error
    def send_finnotech_otp(self, mobile):
        response = self.finnotech_sms_auth.request_sms(
            http_client=self.finnotech_apiclient,
            target_phone=mobile,
            scopes=self.scope,
            redirect_url=self.FINNOTECH_REDIRECT_URL,
        )
        cache.set(
            SESSIN_START_FINNOTECH_CACHE_KEY % self.cache_key_params(mobile),
            timezone.now(),
            3 * 60,
        )
        cache.set(
            OTP_SEND_FINNOTECH_CACHE_KEY % self.cache_key_params(mobile),
            response,
            3 * 60,
        )

    @check_finnotech_timeout(session_cache_key=OTP_SEND_FINNOTECH_CACHE_KEY)
    @handle_finnotech_error
    def verify_finnotech_otp(self, mobile, national_id, otp):
        session = cache.get(
            OTP_SEND_FINNOTECH_CACHE_KEY % self.cache_key_params(mobile)
        )
        session_start = cache.get(
            SESSIN_START_FINNOTECH_CACHE_KEY % self.cache_key_params(mobile)
        )
        response = self.finnotech_sms_auth.verify_sms(
            http_client=self.finnotech_apiclient,
            target_phone=mobile,
            target_national_id=national_id,
            track_id=session.track_id,
            otp=otp,
        )
        cache.set(
            OTP_VERIFY_FINNOTECH_CACHE_KEY % self.cache_key_params(mobile),
            response,
            3 * 60 - (timezone.now() - session_start).seconds,
        )
        return response

    @check_finnotech_timeout(session_cache_key=OTP_VERIFY_FINNOTECH_CACHE_KEY)
    @handle_finnotech_error
    def get_finnotech_authtoken(self, mobile):
        session = cache.get(
            OTP_VERIFY_FINNOTECH_CACHE_KEY % self.cache_key_params(mobile)
        )
        response = self.finnotech_sms_auth.request_token(
            http_client=self.finnotech_apiclient,
            code=session.code,
            redirect_url=self.FINNOTECH_REDIRECT_URL,
        )
        cache.set(
            OTP_TOKEN_FINNOTECH_CACHE_KEY % self.cache_key_params(mobile),
            response,
            60 * 60 * 24,
        )
        return response

    def get_finnotech_endpoint(self):
        """Override this if you want to customize the endpoint input."""
        return self.finnotech_endpoint

    def make_finnotech_request(self, *args, **kwargs):
        method = methodcaller(self.finnotech_endpoint.method_name, *args, **kwargs)
        return method(self.finnotech_apiclient)
