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


from .module_imports import key
from uplink.retry.when import status_5xx


@headers({"Ocp-Apim-Subscription-Key": key})
@retry(max_attempts=20, when=status_5xx())
class _Simple_Forms(Consumer):
    """Inteface to Simple Forms resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    def results(self):
        """Inteface to Sent Emails resource for the RockyRoad API."""
        return self._Results(self)

    def schemas(self):
        """Inteface to Portal Logs resource for the RockyRoad API."""
        return self._Schemas(self)

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class _Results(Consumer):
        """Inteface to Simple Forms Results resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            self._base_url = Resource._base_url
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @http_get("simple-forms/results")
        def list(
            self,
            form_name: Query = None,
            version: Query = None,
        ):
            """This call will return list of resourcess."""

        @returns.json
        @http_get("simple-forms/results/{uid}")
        def get(self, uid: str):
            """This call will get the resources for the specified uid."""

        @delete("simple-forms/results/{uid}")
        def delete(self, uid: str):
            """This call will delete the resources for the specified uid."""

        @returns.json
        @json
        @post("simple-forms/results")
        def insert(self, resource: Body):
            """This call will create the resources with the specified parameters."""

        @json
        @patch("simple-forms/results/{uid}")
        def update(self, uid: str, resource: Body):
            """This call will update the resources with the specified parameters."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class _Schemas(Consumer):
        """Inteface to Simple Forms Results resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            self._base_url = Resource._base_url
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @http_get("simple-forms/schemas")
        def list(
            self,
            form_name: Query = None,
            version: Query = None,
        ):
            """This call will return list of resourcess."""

        @returns.json
        @http_get("simple-forms/schemas/{uid}")
        def get(self, uid: str):
            """This call will get the resources for the specified uid."""

        @delete("simple-forms/schemas/{uid}")
        def delete(self, uid: str):
            """This call will delete the resources for the specified uid."""

        @returns.json
        @json
        @post("simple-forms/schemas")
        def insert(self, resource: Body):
            """This call will create the resources with the specified parameters."""

        @json
        @patch("simple-forms/schemas/{uid}")
        def update(self, uid: str, resource: Body):
            """This call will update the resources with the specified parameters."""
