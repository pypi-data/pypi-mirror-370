import json
import pytest
from pytest_mock import MockerFixture
from iccore.network import HttpClient

TEST_URL = "http://example.com/api"
BASE_HEADERS = {"Authorization": "Bearer token"}
TEST_PAYLOAD = {"key": "value"}


@pytest.fixture
def mock_http_client(mocker: MockerFixture) -> tuple[HttpClient, MockerFixture]:
    client = HttpClient()
    mock_request = mocker.patch.object(client, "_make_request")
    return client, mock_request


def test_post_json(mock_http_client: tuple[HttpClient, MockerFixture]):
    client, mock_request = mock_http_client
    expected_response_data = {"message": "Fake post_json response data"}
    expected_response = {"status": "success", "data": expected_response_data}
    expected_headers = {**BASE_HEADERS, "content-type": "application/json"}

    mock_request.return_value = expected_response

    response = client.post_json(TEST_URL, TEST_PAYLOAD, BASE_HEADERS)

    mock_request.assert_called_once_with(
        TEST_URL,
        "POST",
        expected_headers,
        json.dumps(TEST_PAYLOAD),
    )
    assert response == expected_response


@pytest.mark.parametrize(
    "client_method_name, http_method, send_payload, response_message",
    [
        ("make_get_request", "GET", False, "Fake GET response"),
        ("make_put_request", "PUT", True, "Fake PUT response"),
        ("make_post_request", "POST", True, "Fake POST response"),
    ],
)
def test_standard_http_methods(
    mock_http_client: tuple[HttpClient, MockerFixture],
    client_method_name: str,
    http_method: str,
    send_payload: bool,
    response_message: str,
):
    client, mock_request = mock_http_client
    expected_response_data = {"message": response_message}
    expected_response = {"status": "success", "data": expected_response_data}

    mock_request.return_value = expected_response

    call_args = [TEST_URL, BASE_HEADERS]
    if send_payload:
        call_args.append(TEST_PAYLOAD)

    expected_mock_args = [TEST_URL, http_method, BASE_HEADERS]
    if send_payload:
        expected_mock_args.append(TEST_PAYLOAD)

    client_method_to_call = getattr(client, client_method_name)

    response = client_method_to_call(*call_args)

    mock_request.assert_called_once_with(*expected_mock_args)
    assert response == expected_response
