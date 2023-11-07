from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext_lazy as _

from .utils import get_setting


class AppSettings(object):
    def __init__(self, prefix="FINNOTECH_"):
        self.prefix = prefix

    def _settings(self, name, dflt, *, required=False):
        value = get_setting(self.prefix + name, dflt)
        if required and not value:
            raise ImproperlyConfigured(_("Missing required setting: %s") % name)
        
        return value

    @property
    def CLIENTID(self):
        return self._settings("CLIENT_ID", None, required=True)
    
    @property
    def USERNAME(self):
        return self._settings("USERNAME", None, required=True)
    
    @property
    def PASSWORD(self):
        return self._settings("PASSWORD", None, required=True)
    
    @property
    def REDIRECT_URL(self):
        return self._settings("REDIRECT_URL", None, required=True)


app_settings = AppSettings()
