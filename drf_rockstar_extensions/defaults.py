from django.conf import settings
from django.test.signals import setting_changed
from rest_framework.settings import APISettings

DEFAULTS = {
    # Base API policies
    "FETCHER_FIELDS_AUTHENTICATION_CLASSES": [
        "drf_rockstar_extensions.fields.fetcher_field.utils.auths.BaseAuth"
    ],
}


# List of settings that may be in string import notation.
IMPORT_STRINGS = [
    "FETCHER_FIELDS_AUTHENTICATION_CLASSES",
]


class RockstarSettings(APISettings):
    """Adjustment APISettings from "rest_framework" to support setting drf_rockstar"""

    @property
    def user_settings(self):
        if not hasattr(self, "_user_settings"):
            self._user_settings = getattr(settings, "DRF_ROCKSTAR", {})
        return self._user_settings

    def __check_user_settings(self, user_settings):
        return user_settings


rockstar_settings = RockstarSettings(None, DEFAULTS, IMPORT_STRINGS)


def reload_api_settings(*args, **kwargs):
    setting = kwargs["setting"]
    if setting == "DRF_ROCKSTAR":
        rockstar_settings.reload()


setting_changed.connect(reload_api_settings)
