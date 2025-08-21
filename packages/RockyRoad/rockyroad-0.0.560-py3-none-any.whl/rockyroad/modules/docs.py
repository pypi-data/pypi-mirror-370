from .module_imports import key
from uplink.retry.when import status_5xx
from uplink import (
    get as http_get,
    Consumer,
    returns,
    headers,
    retry,
    Query,
)


@headers({"Ocp-Apim-Subscription-Key": key})
@retry(max_attempts=20, when=status_5xx())
class Docs(Consumer):
    def __init__(self, Resource, *args, **kw):
        super().__init__(base_url=Resource._base_url, *args, **kw)

    @http_get("docs/swagger")
    def swagger(self):
        """This call will return swagger ui."""

    @http_get("docs/redocs")
    def redocs(self):
        """This call will return redoc ui."""

    @returns.json
    @http_get("docs/openapi.json")
    def openapi(self, schema: Query = None, version: Query = None):
        """This call will return OpenAPI json."""
