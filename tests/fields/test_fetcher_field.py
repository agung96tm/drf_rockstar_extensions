# from unittest import TestCase
from django.test import TestCase
from unittest.mock import patch

from requests import HTTPError
from rest_framework import serializers

from drf_rockstar_extensions.fields import FetcherField

FETCH_URL_WITH_PATH_PARAM = "http://localhost:8000/users/{user_id}"


class MockRequests:
    data = {}

    def __init__(self, *args, **kwargs):
        self.data = kwargs.pop("json_data", {})
        super().__init__(*args, **kwargs)

    def json(self):
        return self.data

    @classmethod
    def mock_res_json(cls, json_data):
        return cls(json_data=json_data)


class FetcherFieldTest(TestCase):
    @patch(
        "drf_rockstar_extensions.fields.fetcher_field.fetcher_field.requests.get",
        return_value=MockRequests.mock_res_json(
            {
                "id": 1,
                "is_active": True,
            }
        ),
    )
    def test_success_default_fetcher(self, mock_requests_get):
        field = FetcherField(
            fetch_url=FETCH_URL_WITH_PATH_PARAM,
            path_params={"user_id": "user_id"},
            params={"is_active": "is_active"},
        )
        value = {
            "user_id": 1,
            "is_active": True,
        }
        response = field.to_representation(value)
        self.assertIsNotNone(response)

    @patch(
        "drf_rockstar_extensions.fields.fetcher_field.fetcher_field.requests.get",
        return_value=MockRequests.mock_res_json(
            {
                "data": [
                    {
                        "user": {
                            "id": 1,
                        }
                    }
                ]
            }
        ),
    )
    def test_success_fetcher_look_by_target_source(self, mock_requests_get):
        field = FetcherField(
            fetch_url=FETCH_URL_WITH_PATH_PARAM,
            path_params={"user_id": "user_id"},
            params={"is_active": "is_active"},
            target_source="data.0.user",
        )
        value = {
            "user_id": 1,
            "is_active": True,
        }
        response = field.to_representation(value)
        self.assertEqual(response["id"], 1)

    @patch("drf_rockstar_extensions.fields.fetcher_field.fetcher_field.requests.get")
    def test_success_allow_null_for_http_errors(self, mock_requests_get):
        mock_requests_get.side_effect = HTTPError("Ups, Error happens")
        field = FetcherField(
            fetch_url=FETCH_URL_WITH_PATH_PARAM,
            path_params={"user_id": "user_id"},
            fetch_error_allow_null=True,
            params={"is_active": "is_active"},
            target_source="data.0.user",
        )
        value = {
            "user_id": 1,
            "is_active": True,
        }
        response = field.to_representation(value)
        self.assertIsNone(response)

    # serializers
    @patch(
        "drf_rockstar_extensions.fields.fetcher_field.fetcher_field.requests.get",
        return_value=MockRequests.mock_res_json(
            {"data": [{"user": {"id": 1, "name": "Agung Yuliyanto"}}]}
        ),
    )
    def test_success_use_serializer_as_readable_response(self, mock_requests_get):
        class UserSerializer(serializers.Serializer):
            id = serializers.CharField()
            display_name = serializers.CharField(source="name")

        field = FetcherField(
            fetch_url=FETCH_URL_WITH_PATH_PARAM,
            path_params={"user_id": "user_id"},
            target_source="data.0.user",
            serializer=UserSerializer,
            serializer_kwargs={
                "partial": True,
            },
        )
        value = {
            "user_id": 1,
        }
        response = field.to_representation(value)
        self.assertIsNotNone(response)
        self.assertIsNotNone(response["display_name"], "Agung Yuliyanto")

    @patch(
        "drf_rockstar_extensions.fields.fetcher_field.fetcher_field.requests.get",
        return_value=MockRequests.mock_res_json(
            {"data": [{"user": {"id": 1, "name": "Agung Yuliyanto"}}]}
        ),
    )
    def test_success_use_serializer_with_many_true(self, mock_requests_get):
        class UserSerializer(serializers.Serializer):
            id = serializers.CharField()
            display_name = serializers.CharField(source="name")

        field = FetcherField(
            fetch_url=FETCH_URL_WITH_PATH_PARAM,
            path_params={"user_id": "user_id"},
            target_source="data",
            response_source="user",
            response_source_in_list=True,
            serializer=UserSerializer,
            serializer_kwargs={
                "partial": True,
            },
        )
        value = {
            "user_id": 1,
        }
        response = field.to_representation(value)
        self.assertIsNotNone(response)
        self.assertIsNotNone(len(response), 1)
        self.assertIsNotNone(response[0]["display_name"], "Agung Yuliyanto")
