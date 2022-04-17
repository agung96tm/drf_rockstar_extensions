import requests
from django.utils.translation import gettext_lazy as _
from requests import HTTPError
from requests.exceptions import JSONDecodeError  # noqa
from rest_framework.exceptions import ValidationError
from rest_framework.fields import Field

from drf_rockstar_extensions.settings import api_settings
from .attributes import get_attribute, is_safe_action


class FetcherField(Field):
    default_error_messages = {
        "invalid_server_error": _("Invalid Server Error: {message}")
    }

    def __init__(
        self,
        fetch_url,
        fetch_error_allow_null=True,
        fetch_action="get",
        params=None,
        path_params=None,
        target_source=None,
        serializer=None,
        serializer_as_many=False,
        serializer_kwargs=None,
        response_source=None,
        response_source_in_list=None,
        auth=None,
        auth_kwargs=None,
        *args,
        **kwargs
    ):
        self.fetch_url = fetch_url
        self.fetch_func = getattr(requests, fetch_action)
        self.fetch_error_allow_null = fetch_error_allow_null
        self.is_safe_method = is_safe_action(fetch_action)

        self.serializer = serializer
        self.serializer_kwargs = serializer_kwargs or {}
        self.serializer_as_many = serializer_as_many

        self.params = params or {}
        self.key_params = "params" if self.is_safe_method else "json"

        self.path_params = path_params or {}

        self.target_source = self.init_source(target_source)
        self.response_source = self.init_source(response_source)
        self.response_source_in_list = response_source_in_list

        self.auth = auth or api_settings.DEFAULT_FETCHER_FIELD_AUTH
        self.auth_kwargs = auth_kwargs or {}

        kwargs["source"] = "*"  # force entire object passed to field
        kwargs["read_only"] = True  # force read only
        super().__init__(*args, **kwargs)

    def to_internal_value(self, data):
        return NotImplementedError("Currently to_internal_value unsupported")

    @classmethod
    def init_source(cls, value, as_many=False):
        return value.split(".") if isinstance(value, str) else []

    @classmethod
    def get_params_from_instance(cls, params, instance):
        for key, value in params.items():
            value_from_attributes = get_attribute(instance, [value])
            params[key] = value_from_attributes or value
        return params

    def get_url(self, value):
        return {
            "url": self.fetch_url.format(
                **self.get_params_from_instance(self.path_params, value)
            )
        }

    def get_params(self, value):
        return {self.key_params: self.get_params_from_instance(self.params, value)}

    def get_auth(self, obj):
        if callable(self.auth):
            return self.auth(self, obj, self.context.get("request"), **self.auth_kwargs)
        return self.auth or {}

    def run_fetcher(self, value):
        response = None
        try:
            response = self.fetch_func(
                **self.get_url(value),
                **self.get_params(value),
                **self.get_auth(value),
            ).json()
        except HTTPError as e:
            if not self.fetch_error_allow_null:
                raise ValidationError(
                    self.default_error_messages["invalid_server_error"].format(
                        message=str(e)
                    )
                )
        except JSONDecodeError as e:  # fail decode json
            response = str(e)
        return response

    def run_target_source(self, value):
        if self.target_source is not None:
            value = get_attribute(value, self.target_source)
        return value

    def run_response_source(self, value):
        if self.response_source is not None:
            if self.response_source_in_list:
                value = [get_attribute(v, self.response_source) for v in value]
            else:
                value = get_attribute(value, self.response_source)
        return value

    def run_serializer(self, value):
        if self.serializer is not None:
            kwargs = self.serializer_kwargs
            kwargs.setdefault("many", isinstance(value, list))
            value = self.serializer(value, context=self.context, **kwargs).data
        return value

    def to_representation(self, value):
        value = self.run_fetcher(value)
        value = self.run_target_source(value)
        value = self.run_response_source(value)
        value = self.run_serializer(value)
        return value
