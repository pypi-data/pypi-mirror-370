import json
import os

import requests

from geodesic.config import ConfigManager
from geodesic.auth import get_auth_manager
from requests.adapters import HTTPAdapter, Retry

DEBUG = os.getenv("DEBUG", "false")

if DEBUG.lower() in ("1", "true", "yes", "external"):
    DEBUG = True
else:
    DEBUG = False

API_VERSION = 1
client = None


def get_client():
    """Get the current client instance. If none exists, create one."""
    global client
    if client is not None:
        return client

    client = Client()
    return client


def raise_on_error(res: requests.Response) -> requests.Response:
    """Checks a Response for errors. Returns the original Response if none are found."""
    if res.status_code >= 400:
        try:
            res_json = res.json()
            if "error" in res_json:
                msg = res_json["error"]
                returnError = msg
                if msg is not None:
                    if "detail" in msg:
                        returnError = msg["detail"]
                    if "instance" in msg:
                        returnError += f'\nrequest-id: {msg["instance"]}'
                raise requests.exceptions.HTTPError(returnError)
            else:
                raise requests.exceptions.HTTPError(res.text)
        except json.decoder.JSONDecodeError:
            raise requests.exceptions.HTTPError(res.text)
    return res


class Client:
    """Rest client interface for geodesic backend.

    Used to interface with the Geodesic Platform by implementing the Rest API.
    """

    def __init__(self):
        self._auth = get_auth_manager()
        self._conf = ConfigManager()
        self._conf.get_active_config()
        self._session = None
        self._api_version = API_VERSION
        self._additional_headers = {}

    def request(self, uri, method="GET", **params):
        # Get the active config, this could have been switched at runtime.
        # Note: doesn't sync with config file, must be explicitly reloaded.
        cfg = self._conf.get_active_config()

        url = cfg.host
        if url.endswith("/"):
            url = url[:-1]

        send_auth_headers = False

        # Route request to correct endpoint
        if uri.startswith("/spacetime"):
            uri = uri.replace("/spacetime", "", 1)
            url = f"{cfg.service_host('spacetime')}{uri}"
            send_auth_headers = True
        elif uri.startswith("/boson"):
            uri = uri.replace("/boson", "", 1)
            url = f"{cfg.service_host('boson')}{uri}"
            send_auth_headers = True
        elif uri.startswith("/entanglement"):
            uri = uri.replace("/entanglement", "", 1)
            url = f"{cfg.service_host('entanglement')}{uri}"
            send_auth_headers = True
        elif uri.startswith("/tesseract"):
            uri = uri.replace("/tesseract", "", 1)
            url = f"{cfg.service_host('tesseract')}{uri}"
            send_auth_headers = True
        elif uri.startswith("/krampus"):
            uri = uri.replace("/krampus", "", 1)
            url = f"{cfg.service_host('krampus')}{uri}"
            send_auth_headers = True
        elif uri.startswith("/ted"):
            uri = uri.replace("/ted", "", 1)
            uri = f"{cfg.service_host('ted')}{uri}"
            send_auth_headers = True
        elif uri.startswith("/flock"):
            uri = uri.replace("/flock", "", 1)
            uri = f"{cfg.service_host('flock')}{uri}"
            send_auth_headers = True
        elif uri.startswith("/vertex"):
            uri = uri.replace("/vertex", "", 1)
            uri = f"{cfg.service_host('vertex')}{uri}"
            send_auth_headers = True
        elif uri.startswith("/"):
            url = url + uri

        if uri.startswith("http"):
            url = uri
            send_auth_headers = cfg.send_headers(url)

        if method == "GET":
            req = requests.Request("GET", url, params=params)
        elif method == "POST":
            body = params.get("__bytes", None)
            if body is not None:
                req = requests.Request("POST", url, data=body)
            else:
                req = requests.Request("POST", url, json=params)
        elif method == "PUT":
            body = params.get("__bytes", None)
            if body is not None:
                req = requests.Request("PUT", url, data=body)
            else:
                req = requests.Request("PUT", url, json=params)
        elif method == "DELETE":
            body = params.get("__body", None)
            if body is not None:
                req = requests.Request("DELETE", url, json=body)
            else:
                req = requests.Request("DELETE", url, params=params)
        elif method == "PATCH":
            body = params.get("__body", None)
            if body is not None:
                req = requests.Request("PATCH", url, json=body)
            else:
                req = requests.Request("PATCH", url, params=params)
        else:
            raise Exception(f"unknown method: {method}")

        # Only send headers for requests to our services, but client could be used instead of
        # requests if you choose.
        if send_auth_headers:
            req.headers["Authorization"] = "Bearer {0}".format(self._auth.id_token)
            req.headers["X-Auth-Request-Access-Token"] = "Bearer {0}".format(
                self._auth.access_token
            )
            for k, v in self._additional_headers.items():
                req.headers[k] = v
            self._additional_headers = {}

        if self._session is None:
            s = requests.Session()
            retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[502, 503, 504])
            s.mount("http://", HTTPAdapter(max_retries=retries))
            s.mount("https://", HTTPAdapter(max_retries=retries))
            self._session = s

        prepped = req.prepare()

        # get user environment settings
        settings = self._session.merge_environment_settings(prepped.url, {}, None, None, None)
        res = self._session.send(prepped, **settings)

        return res

    def add_request_headers(self, headers):
        self._additional_headers.update(headers)

    def get(self, uri, **query):
        return self.request(uri, method="GET", **query)

    def post(self, uri, **body):
        return self.request(uri, method="POST", **body)

    def post_bytes(self, uri, body):
        if not isinstance(body, bytes):
            raise TypeError("body must be bytes")
        return self.request(uri, method="POST", __bytes=body)

    def put(self, uri, **body):
        return self.request(uri, method="PUT", **body)

    def put_bytes(self, uri, body):
        if not isinstance(body, bytes):
            raise TypeError("body must be bytes")
        return self.request(uri, method="PUT", __bytes=body)

    def delete(self, uri, **query):
        return self.request(uri, method="DELETE", **query)

    def delete_with_body(self, uri, **body):
        return self.request(uri, method="DELETE", __body=body)

    def patch(self, uri, **params):
        return self.request(uri, method="PATCH", **params)

    def patch_with_body(self, uri, **body):
        return self.request(uri, method="PATCH", __body=body)
