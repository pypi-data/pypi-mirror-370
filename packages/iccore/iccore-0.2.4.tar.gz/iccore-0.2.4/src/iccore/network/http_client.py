"""
A basic low-dependency http client
"""

import urllib.request
import urllib.parse
from pathlib import Path
import os
import json

from iccore.runtime import ctx


class HttpClient:
    """
    A basic http client with low dependencies (urllib)
    """

    def __init__(self):
        self.default_encode_charset = "utf-8"
        self.default_decode_charset = "utf-8"

    def post_json(self, url: str, payload, headers: dict[str, str] | None):
        if not headers:
            headers = {}

        headers["content-type"] = "application/json"
        return self.make_post_request(url, headers, json.dumps(payload))

    def make_get_request(self, url: str, headers: dict[str, str] | None = None):
        if not headers:
            headers = {}
        return self._make_request(url, "GET", headers)

    def make_put_request(
        self, url: str, headers: dict[str, str] | None = None, payload=None
    ):
        if not headers:
            headers = {}
        return self._make_request(url, "PUT", headers, payload)

    def make_post_request(
        self, url: str, headers: dict[str, str] | None = None, payload=None
    ):
        if not headers:
            headers = {}
        return self._make_request(url, "POST", headers, payload)

    def download_file(
        self, url: str, path: Path, headers: dict[str, str] | None = None
    ):
        if not headers:
            headers = {}

        if not ctx.can_read():
            ctx.add_cmd(f"download file {url} {path} {headers}")

        with open(path, "wb") as f:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response:
                self._check_http_status(response)
                f.write(response.read())

    def upload_file(self, url: str, path: Path, headers: dict[str, str] | None = None):

        if not headers:
            headers = {}

        if not ctx.can_modify():
            ctx.add_cmd(f"upload file {url} {path} {headers}")
            return ""

        if not path.exists():
            raise RuntimeError(f"Attempted to upload file without valid path: {path}")

        headers["Content-Length"] = str(os.stat(path).st_size)
        headers["Content-Type"] = "application/octet-stream"

        with open(path, "rb") as f:
            req = urllib.request.Request(url, headers=headers, data=f, method="PUT")
            with urllib.request.urlopen(req) as response:
                self._check_http_status(response)
                response_str = response.read().decode(self._get_charset(response))
        return response_str

    def _make_request(
        self, url: str, method: str, headers: dict[str, str] | None = None, payload=None
    ):

        if not headers:
            headers = {}

        if method == "GET":
            if not ctx.can_read():
                ctx.add_cmd(f"make_request GET {url} {headers}")
                return ""
        elif method in ["PUT", "POST"]:
            if not ctx.can_modify():
                ctx.add_cmd(f"make_request {method} {url} {headers} {payload}")
                return ""

        req = urllib.request.Request(
            url, headers=headers, data=self._endcode_payload(payload), method=method
        )
        with urllib.request.urlopen(req) as response:
            self._check_http_status(response)
            response_str = response.read().decode(self._get_charset(response))
        return response_str

    def _check_http_status(self, response):
        if response.status >= 300:
            body = response.read().decode(self._get_charset(response))
            msg = f"code {response.status}, reason {response.reason}, and body {body}"
            raise RuntimeError(f"Http Request failed with: {msg}")

    def _endcode_payload(self, payload):
        if not payload:
            return payload
        return payload.encode("utf-8")

    def _get_charset(self, response):
        charset = response.headers.get_content_charset()
        if not charset:
            charset = "utf-8"
        return charset
