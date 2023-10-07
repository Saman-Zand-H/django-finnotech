from functools import wraps
from logging import getLogger

from django.contrib import messages
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .constants import SESSIN_START_FINNOTECH_CACHE_KEY
from .pyfinnotech.exceptions import FinnotechHttpException

logger = getLogger(__file__)


def handle_finnotech_error(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FinnotechHttpException as e:
            request = args[0].request
            logger.error(
                f"An error occurred while {request.user.username} was requesting for otp: {e}"
            )
            msg = _("Something went wrong while validating your information.")
            messages.error(request, msg)
            raise ValidationError(msg)

    return wrapper


def validate_finnotech_form(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # we can't pop from tuples, so we turn it into a list
        args = list(args)
        try:
            return func(*args, **kwargs)
        except (FinnotechHttpException, ValidationError):
            self = args.pop(0)
            messages.error(
                self.request, _("There was and error connecting to Finnotech.")
            )
            return self.form_invalid(*args, **kwargs)

    return wrapper


def check_finnotech_timeout(session_cache_key, scope=None):
    def _check_finnotech_timeout(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            self = args[0]
            mobile = self.request.session.get("mobile")

            if not (
                cache.get(session_cache_key % self.cache_key_params(mobile))
                and (
                    session_start := cache.get(
                        SESSIN_START_FINNOTECH_CACHE_KEY
                        % {
                            "scope": scope or self.scope,
                            "mobile": self.request.session.get("mobile"),
                        }
                    )
                )
            ):
                msg = _("Your authorization session has expired or does not exist.")
                messages.error(self.request, msg)
                raise ValidationError(msg)

            if (timezone.now() - session_start).seconds >= 3 * 60:
                msg = _("Your session has expired.")
                messages.error(self.request, msg)
                raise ValidationError(msg)

            return func(*args, **kwargs)

        return wrapper

    return _check_finnotech_timeout
