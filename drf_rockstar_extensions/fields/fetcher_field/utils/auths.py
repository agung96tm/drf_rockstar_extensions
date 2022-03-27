from django.core.cache import cache

from drf_rockstar_extensions.defaults import rockstar_settings


class BaseAuth:
    name = None

    def __init__(self, request, **kwargs):
        self.request = request
        self.kwargs = kwargs

    @classmethod
    def get_auth(cls, **kwargs):
        return {}


class BasicAuth(BaseAuth):
    name = "basic"

    @classmethod
    def get_auth(cls, **kwargs):
        return {"auth": (None, None)}


def get_auth_class_by_name(name):
    authentication_classes = cache.get("drf_rockstar_fetcher_fields_auth_classes")
    if authentication_classes is None:
        authentication_classes = (
            rockstar_settings.FETCHER_FIELDS_AUTHENTICATION_CLASSES or []
        )
        authentication_classes = {
            authentication_class.name: authentication_class
            for authentication_class in authentication_classes
        }
        cache.set(
            "drf_rockstar_fetcher_fields_auth_classes", authentication_classes, 1200
        )
    return authentication_classes.get(name)
