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
class Warranty_Registrations(Consumer):
    """Inteface to warranty registrations resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    @returns.json
    @http_get("warranties/registrations")
    def list(
        self,
    ):
        """This call will return warranty registration information for the specified criteria."""

    @returns.json
    @http_get("warranties/registrations/{uid}")
    def get(
        self,
        uid: str
    ):
        """This call will return warranty registration information for the specified criteria."""

    @returns.json
    @http_get("warranties/registrations/machine/{machine_uid}")
    def get_by_machine(
        self,
        machine_uid: str
    ):
        """This call will return warranty registration information for the specified criteria."""

    @returns.json
    @delete("warranties/registrations/{uid}")
    def delete(self, uid: str):
        """This call will delete the warranty registration information for the specified uid."""

    @returns.json
    @json
    @post("warranties/registrations/{dealer_uid}")
    def insert(self, warranty_registration: Body, dealer_uid: str, company_uid: Query = None):
        """This call will create warranty registration information with the specified parameters."""

    @returns.json
    @json
    @patch("warranties/registrations/{uid}")
    def update(self, warranty_registration: Body, uid: str):
        """This call will update the warranty registration information with the specified parameters."""
