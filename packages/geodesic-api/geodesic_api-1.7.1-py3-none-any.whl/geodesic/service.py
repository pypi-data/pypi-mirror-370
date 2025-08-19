from geodesic import get_client


class ServiceClient:
    def __init__(self, name: str, version: int = 1, api: str = None, **extra):
        self.name = name
        self.version = version
        self._stub = f"/{name}/api/v{version}"
        if api is not None:
            self._stub += "/" + api

        self.extra = {}
        self.extra.update(extra)

    def add_request_headers(self, headers):
        get_client().add_request_headers(headers)

    def add_extra(self, **extra):
        self.extra.update(extra)

    def get(self, resource="", **query):
        if not resource.startswith("/") and resource != "":
            resource = "/" + resource
        params = {}
        params.update(self.extra)
        params.update(query)
        return get_client().get(self._stub + resource, **params)

    def delete(self, resource="", **query):
        if not resource.startswith("/") and resource != "":
            resource = "/" + resource
        params = {}
        params.update(self.extra)
        params.update(query)
        return get_client().delete(self._stub + resource, **params)

    def delete_with_body(self, resource="", **body):
        if not resource.startswith("/") and resource != "":
            resource = "/" + resource
        params = {}
        params.update(self.extra)
        params.update(body)
        return get_client().delete_with_body(self._stub + resource, **params)

    def put(self, resource="", **body):
        if not resource.startswith("/") and resource != "":
            resource = "/" + resource
        params = {}
        params.update(self.extra)
        params.update(body)
        return get_client().put(self._stub + resource, **params)

    def put_bytes(self, resource="", body: bytes = None):
        if not resource.startswith("/") and resource != "":
            resource = "/" + resource
        return get_client().put_bytes(self._stub + resource, body)

    def post(self, resource="", **body):
        if not resource.startswith("/") and resource != "":
            resource = "/" + resource
        params = {}
        params.update(self.extra)
        params.update(body)
        return get_client().post(self._stub + resource, **params)

    def post_bytes(self, resource="", body: bytes = None):
        if not resource.startswith("/") and resource != "":
            resource = "/" + resource
        return get_client().post_bytes(self._stub + resource, body)

    def patch(self, resource="", **body):
        if not resource.startswith("/") and resource != "":
            resource = "/" + resource
        params = {}
        params.update(self.extra)
        params.update(body)
        return get_client().patch(self._stub + resource, **params)

    def patch_with_body(self, resource="", **body):
        if not resource.startswith("/") and resource != "":
            resource = "/" + resource
        params = {}
        params.update(self.extra)
        params.update(body)
        return get_client().patch_with_body(self._stub + resource, **params)
