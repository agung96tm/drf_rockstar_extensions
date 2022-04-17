from django.conf import settings
from django.test.signals import setting_changed
from rest_framework.settings import APISettings


USER_SETTINGS = getattr(settings, "DRF_ROCKSTAR", None)

DEFAULTS = {
    "DEFAULT_FETCHER_FIELD_AUTH": "drf_rockstar_extensions.fields.fetcher_field.basic_auth"
}

IMPORT_STRINGS = ["DEFAULT_FETCHER_FIELD_AUTH"]


class RockstarSettings(APISettings):
    @property
    def user_settings(self):
        if not hasattr(self, "_user_settings"):
            self._user_settings = getattr(settings, "DRF_ROCKSTAR_EXTENSIONS", {})
        return self._user_settings

    def __check_user_settings(self, user_settings):
        return user_settings


api_settings = APISettings(USER_SETTINGS, DEFAULTS, IMPORT_STRINGS)


def reload_api_settings(*args, **kwargs):  # pragma: no cover
    global api_settings

    setting, value = kwargs["setting"], kwargs["value"]

    if setting == "DRF_ROCKSTAR":
        api_settings = APISettings(value, DEFAULTS, IMPORT_STRINGS)


setting_changed.connect(reload_api_settings)
