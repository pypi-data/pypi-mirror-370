import pytest

from iccore.network import HttpClient


def test_get_request():

    url = "bad_url"
    client = HttpClient()

    with pytest.raises(ValueError):
        client.make_get_request(url)
