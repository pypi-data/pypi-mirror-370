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
class Engines(Consumer):
    """Inteface to Inspection resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    def catalog(self):
        return self.__Catalog(self)

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class __Catalog(Consumer):
        """Inteface to Warranty Credit Request resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @http_get("engines/catalog/vendors")
        def vendors(
            self,
        ):
            """This call will return specified info for the specified criteria."""

        @returns.json
        @http_get("engines/catalog/{uid}")
        def get(
            self,
            uid: str
        ):
            """This call will return specified info for the specified criteria."""

        @returns.json
        @http_get("engines/catalog")
        def list(
            self,
            vendor: Query = None,
        ):
            """This call will return specified info for the specified criteria."""

        @returns.json
        @json
        @post("engines/catalog")
        def insert(self, engine_catalog: Body):
            """This call will create specified info with the specified parameters."""

        @delete("engines/catalog/{uid}")
        def delete(self, uid: str):
            """This call will delete specified info for the specified uid."""

        @json
        @patch("engines/catalog/{uid}")
        def update(self, uid: str, engine_catalog: Body):
            """This call will update specified info with the specified parameters."""

    @returns.json
    @json
    @post("engines")
    def insert(self, engine_and_machine: Body):
        """This call will create specified info with the specified parameters."""

    @returns.json
    @http_get("engines")
    def list(
        self,
        machine_uid: Query = None,
    ):
        """This call will return specified info for the specified criteria."""

    @returns.json
    @http_get("engines/{uid}")
    def get(self, uid: str):
        """This call will return specified info for the specified criteria."""

    @delete("engines/{uid}")
    def delete(self, uid: str):
        """This call will delete specified info for the specified uid."""

    @json
    @patch("engines/{uid}")
    def update(self, uid: str, engine_and_machine: Body):
        """This call will update specified info with the specified parameters."""
