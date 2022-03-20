import requests
from requests import HTTPError
from requests.exceptions import JSONDecodeError  # noqa
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _

from rest_framework.fields import Field
from rest_framework.exceptions import ValidationError

from drf_rockstar_extensions import defaults
from drf_rockstar_extensions.fields.fetcher_field.extras.helpers import (
    get_attribute, is_safe_action,
)


class FetcherField(Field):
    default_error_messages = {
        'invalid_server_error': _('Invalid Server Error: {message}')
    }

    def __init__(self,
                 fetch_url,
                 action='get',
                 params=None,
                 path_params=None,
                 response_source=None,
                 auth='default',
                 auth_kwargs=None,
                 *args,
                 **kwargs):
        self.fetch_url = fetch_url
        self.fetch_func = getattr(requests, action)
        self.is_safe_method = is_safe_action(action)

        self.params = params or {}
        self.key_params = 'params' if self.is_safe_method else 'json'

        self.path_params = path_params or {}

        self.response_source = (
            response_source.split('.')
            if isinstance(response_source, str) else None
        )

        self.auth = auth
        self.auth_kwargs = auth_kwargs or {}

        kwargs['source'] = '*'  # force entire object passed to field
        kwargs['read_only'] = True  # force read only
        super().__init__(*args, **kwargs)

    def to_internal_value(self, data):
        return NotImplementedError('Currently to_internal_value not supported')

    @classmethod
    def get_params_from_instance(cls, params, instance):
        for key, value in params.items():
            value_from_attributes = get_attribute(instance, [value])
            params[key] = (
                value_from_attributes
                if value_from_attributes is not None else
                value
            )
        return params

    def get_url(self, value):
        return {
            'url': self.fetch_url.format(
                **self.get_params_from_instance(self.path_params, value)
            )
        }

    def get_params(self, value):
        return {
            self.key_params: self.get_params_from_instance(self.params, value)
        }

    def get_auth(self, obj):
        AuthClass = import_string(
            defaults.DRF_ROCKSTAR_FETCHER_FIELDS.get(
                'authentication_classes', {}
            )[self.auth]
        )

        if AuthClass is not None:
            return AuthClass(
                request=self.context.get('request'),
                **self.get_params_from_instance(self.auth_kwargs, obj)
            ).get_auth()
        return {}

    def run_fetcher(self, value):
        try:
            response = self.fetch_func(
                **self.get_url(value),
                **self.get_params(value),
                **self.get_auth(value),
            ).json()
        except HTTPError as e:
            raise ValidationError(
                self.default_error_messages['invalid_server_error'].format(
                    message=str(e)
                )
            )
        except JSONDecodeError:  # fail decode json
            response = None
        return response

    def run_response_source(self, value):
        if self.response_source is not None:
            value = get_attribute(value, self.response_source)
        return value

    def to_representation(self, value):
        value = self.run_fetcher(value)
        value = self.run_response_source(value)
        return value
