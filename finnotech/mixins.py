from functools import wraps
from logging import getLogger
from operator import methodcaller

from django.contrib import messages
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic.edit import FormMixin

from .app_settings import app_settings as settings
from .constants import (
    OTP_SEND_FINNOTECH_CACHE_KEY,
    OTP_TOKEN_FINNOTECH_CACHE_KEY,
    OTP_VERIFY_FINNOTECH_CACHE_KEY,
    SESSION_START_FINNOTECH_CACHE_KEY,
    SMS_AUTH_ENDPOINT_SESSION_KEY,
    SMS_AUTH_REQUEST_TTL,
    SMS_AUTH_TOKEN_TTL,
    FinnotechEndpoint,
)
from .pyfinnotech.api import FinnotechApiClient
from .pyfinnotech.exceptions import FinnotechHttpException
from .pyfinnotech.token import SmsAuthorization

logger = getLogger(__name__)


def handle_finnotech_error(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except FinnotechHttpException as e:
            request = self.request
            logger.error(f"An error occurred while {request.user.username} was requesting for otp: {e}")
            msg = _("Something went wrong while validating your information.")
            messages.error(request, msg)
            raise ValidationError(msg)

    return wrapper


def validate_finnotech_form(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (FinnotechHttpException, ValidationError):
            messages.error(self.request, _("There was and error connecting to Finnotech."))
            self.request.session.delete(SMS_AUTH_ENDPOINT_SESSION_KEY)
            return self.form_invalid(self, *args, **kwargs)

    return wrapper


def check_finnotech_timeout(session_cache_key, scope=None):
    def _check_finnotech_timeout(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            mobile = self.request.session.get("mobile")

            if not (
                cache.get(self.get_finnotech_cache_key(session_cache_key, mobile))
                and (
                    session_start := cache.get(self.get_finnotech_cache_key(SESSION_START_FINNOTECH_CACHE_KEY, mobile))
                )
            ):
                msg = _("Your authorization session has expired or does not exist.")
                messages.error(self.request, msg)
                raise ValidationError(msg)

            if self.remained_request_ttl(session_start) <= 0:
                msg = _("Your session has expired.")
                messages.error(self.request, msg)
                raise ValidationError(msg)

            return func(self, *args, **kwargs)

        return wrapper

    return _check_finnotech_timeout


class FinnotechClientAuthMixin:
    finnotech_endpoint: FinnotechEndpoint = None

    def setup_finnotech(self):
        self.FINNOTECH_CLIENTID = settings.CLIENTID
        self.FINNOTECH_USERNAME = settings.USERNAME
        self.FINNOTECH_PASSWORD = settings.PASSWORD
        self.FINNOTECH_REDIRECT_URL = settings.REDIRECT_URL

        self.finnotech_endpoint = self.get_finnotech_endpoint()
        self.scope = self.finnotech_endpoint.scope
        self.finnotech_apiclient = FinnotechApiClient(
            client_id=self.FINNOTECH_CLIENTID,
            client_national_id=self.FINNOTECH_USERNAME,
            client_secret=self.FINNOTECH_PASSWORD,
            scopes=[self.finnotech_endpoint.scope],
        )
        self.finnotech_sms_auth = SmsAuthorization
        self.get_finnotech_cache_key = lambda key_name, mobile: key_name % self.cache_key_params(mobile)
        self.cache_key_params = lambda i: {"scope": self.scope, "mobile": i}

    def get_cache_key(self, mobile):
        return OTP_TOKEN_FINNOTECH_CACHE_KEY % self.cache_key_params(mobile)

    def dispatch(self, request, *args, **kwargs):
        self.setup_finnotech()
        return super().dispatch(request, *args, **kwargs)

    def remained_request_ttl(self, start):
        return SMS_AUTH_REQUEST_TTL - (timezone.now() - start).seconds

    @handle_finnotech_error
    def send_finnotech_otp(self, mobile):
        response = self.finnotech_sms_auth.request_sms(
            http_client=self.finnotech_apiclient,
            target_phone=mobile,
            scopes=self.scope,
            redirect_url=self.FINNOTECH_REDIRECT_URL,
        )

        cache.set(
            self.get_finnotech_cache_key(SESSION_START_FINNOTECH_CACHE_KEY, mobile),
            timezone.now(),
            SMS_AUTH_REQUEST_TTL,
        )
        cache.set(
            self.get_finnotech_cache_key(OTP_SEND_FINNOTECH_CACHE_KEY, mobile),
            response,
            SMS_AUTH_REQUEST_TTL,
        )

    @check_finnotech_timeout(session_cache_key=OTP_SEND_FINNOTECH_CACHE_KEY)
    @handle_finnotech_error
    def verify_finnotech_otp(self, mobile, national_id, otp):
        session = cache.get(self.get_finnotech_cache_key(OTP_SEND_FINNOTECH_CACHE_KEY, mobile))
        session_start = cache.get(self.get_finnotech_cache_key(SESSION_START_FINNOTECH_CACHE_KEY, mobile))

        response = self.finnotech_sms_auth.verify_sms(
            http_client=self.finnotech_apiclient,
            target_phone=mobile,
            target_national_id=national_id,
            track_id=session.track_id,
            otp=otp,
        )

        cache.set(
            self.get_finnotech_cache_key(OTP_VERIFY_FINNOTECH_CACHE_KEY, mobile),
            response,
            self.remained_request_ttl(session_start),
        )
        return response

    @check_finnotech_timeout(session_cache_key=OTP_VERIFY_FINNOTECH_CACHE_KEY)
    @handle_finnotech_error
    def get_finnotech_authtoken(self, mobile):
        session = cache.get(self.get_finnotech_cache_key(OTP_VERIFY_FINNOTECH_CACHE_KEY, mobile))
        response = self.finnotech_sms_auth.request_token(
            http_client=self.finnotech_apiclient,
            code=session.code,
            redirect_url=self.FINNOTECH_REDIRECT_URL,
        )

        cache.set(
            self.get_finnotech_cache_key(OTP_TOKEN_FINNOTECH_CACHE_KEY, mobile),
            response,
            SMS_AUTH_TOKEN_TTL,
        )
        return response

    @validate_finnotech_form
    def post(self, *args, **kwargs):
        return super().post(*args, **kwargs)

    def get_finnotech_endpoint(self):
        """Override this if you want to customize the endpoint input."""
        return self.finnotech_endpoint

    def make_finnotech_request(self, *args, **kwargs):
        method = methodcaller(self.finnotech_endpoint.method_name, *args, **kwargs)
        return method(self.finnotech_apiclient)
