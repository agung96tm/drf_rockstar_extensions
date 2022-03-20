import json
from unittest import TestCase
from unittest.mock import patch

from drf_rockstar_extensions.fields import FetcherField


FETCH_URL_WITH_PATH_PARAM = 'http://localhost:8000/users/{user_id}'


class MockRequests:
    data = {}

    def __init__(self, *args, **kwargs):
        self.data = kwargs.pop('json_data', {})
        super().__init__(*args, **kwargs)

    def json(self):
        return self.data

    @classmethod
    def mock_res_json(cls, json_data):
        return cls(json_data=json_data)


class FetcherFieldTest(TestCase):
    @patch(
        'drf_rockstar_extensions.fields.fetcher_field.fetcher_field.requests.get',
        return_value=MockRequests.mock_res_json({
            'id': 1,
            'is_active': True,
        })
    )
    def test_success_default_fetcher(self, mock_requests_get):
        field = FetcherField(
            fetch_url=FETCH_URL_WITH_PATH_PARAM,
            path_params={'user_id': 'user_id'},
            params={'is_active': 'is_active'},
        )
        value = {
            'user_id': 1,
            'is_active': True,
        }
        response = field.to_representation(value)
        self.assertIsNotNone(response)

    @patch(
        'drf_rockstar_extensions.fields.fetcher_field.fetcher_field.requests.get',
        return_value=MockRequests.mock_res_json({
            'data': [
                {
                    'user': {
                        'id': 1,
                    }
                }
            ]
        })
    )
    def test_success_fetcher_look_by_response_source(self, mock_requests_get):
        field = FetcherField(
            fetch_url=FETCH_URL_WITH_PATH_PARAM,
            path_params={'user_id': 'user_id'},
            params={'is_active': 'is_active'},
            response_source='data.0.user'
        )
        value = {
            'user_id': 1,
            'is_active': True,
        }
        response = field.to_representation(value)
        self.assertIsNotNone(response)
        self.assertEqual(response['id'], 1)
