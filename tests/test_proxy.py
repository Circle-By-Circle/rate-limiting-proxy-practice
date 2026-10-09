"""Baseline proxy tests. Add rate-limiting tests during the exercise."""
from io import BytesIO
from types import SimpleNamespace

import pytest
import requests

from proxy.app import create_app


class Transport:
    def __init__(self):
        self.calls = []
        self.error = None
        self.response = SimpleNamespace(
            status_code=200, headers={"Content-Type": "application/json"},
            raw=SimpleNamespace(read=lambda decode_content=False: b'{"ok":true}'),
            close=lambda: None,
        )

    def request(self, **kwargs):
        self.calls.append(kwargs)
        if self.error:
            raise self.error
        return self.response


@pytest.fixture
def setup():
    transport = Transport()
    app = create_app("http://upstream.test", transport)
    app.config["TESTING"] = True
    return app.test_client(), transport


def test_health_is_local(setup):
    client, transport = setup
    assert client.get("/health").get_json()["service"] == "proxy"
    assert transport.calls == []


def test_forwards_path_and_repeated_query_parameters(setup):
    client, transport = setup
    response = client.get("/echo?tag=a&tag=b")
    assert response.status_code == 200
    assert response.get_json() == {"ok": True}
    call = transport.calls[0]
    assert call["url"] == "http://upstream.test/echo"
    assert call["params"] == [("tag", "a"), ("tag", "b")]
    assert call["allow_redirects"] is False
    assert call["timeout"] == 5


@pytest.mark.parametrize("method", ["POST", "PUT", "PATCH", "DELETE"])
def test_forwards_method_body_and_client_header(setup, method):
    client, transport = setup
    client.open("/echo", method=method, data=b"hello", headers={"X-Client-ID": "alice"})
    call = transport.calls[0]
    assert call["method"] == method
    assert call["data"] == b"hello"
    assert call["headers"]["X-Client-Id"] == "alice"


def test_removes_connection_specific_request_headers(setup):
    client, transport = setup
    client.get("/items", headers={"Connection": "X-Internal", "X-Internal": "secret"})
    headers = {key.lower(): value for key, value in transport.calls[0]["headers"].items()}
    assert "connection" not in headers
    assert "x-internal" not in headers
    assert "host" not in headers


def test_preserves_upstream_status_and_response_headers(setup):
    client, transport = setup
    transport.response.status_code = 503
    transport.response.headers = {"Content-Type": "text/plain", "X-Upstream": "demo",
                                  "Connection": "X-Internal", "X-Internal": "secret"}
    response = client.get("/items")
    assert response.status_code == 503
    assert response.headers["X-Upstream"] == "demo"
    assert "X-Internal" not in response.headers


@pytest.mark.parametrize("error,status", [(requests.Timeout(), 504), (requests.ConnectionError(), 502)])
def test_upstream_failure(setup, error, status):
    client, transport = setup
    transport.error = error
    assert client.get("/items").status_code == status
