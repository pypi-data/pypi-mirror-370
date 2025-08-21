from .module_imports import key
from uplink.retry.when import status_5xx
from uplink import (
    Consumer,
    get as http_get,
    post,
    patch,
    delete,
    returns,
    headers,
    retry,
    Body,
    json,
    Query,
)


@headers({"Ocp-Apim-Subscription-Key": key})
@retry(max_attempts=20, when=status_5xx())
class GL_Codes(Consumer):
    """Inteface to Warranties GL Codes resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    @returns.json
    @http_get("warranties/gl-codes")
    def list(self, site: Query = None):
        """This call will return list of specified GL codes."""

    @returns.json
    @http_get("warranties/gl-codes/{uid}")
    def get(self, uid: str):
        """This call will return the specified GL code."""

    @delete("warranties/gl-codes/{uid}")
    def delete(self, uid: str):
        """This call will delete the warranty GL code for the specified uid."""

    @returns.json
    @json
    @post("warranties/gl-codes")
    def insert(self, warranty_gl_code: Body):
        """This call will create warranty GL code with the specified parameters."""

    @json
    @patch("warranties/gl-codes/{uid}")
    def update(self, uid: str, warranty_gl_code: Body):
        """This call will update the warranty GL code with the specified parameters."""
