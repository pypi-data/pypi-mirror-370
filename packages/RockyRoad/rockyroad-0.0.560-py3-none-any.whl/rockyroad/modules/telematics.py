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
class Telematics(Consumer):
    """Inteface to Telematics resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    @returns.json
    @http_get("machines/telematics")
    def list(
        self,
        uid: Query = None,
        machine_uid: Query = None,
    ):
        """This call will return telematics information for the specified criteria."""

    @returns.json
    @http_get("machines/telematics/{uid}")
    def get(
        self,
        uid
    ):
        """This call will return the telematics resource for the specified uid."""

    @returns.json
    @http_get("machines/telematics/machine/{uid}")
    def get_by_machine_uid(
        self,
        uid
    ):
        """This call will return the telematics resource for the specified machine uid."""

    @returns.json
    @http_get("machines/telematics/model/{model}/serial/{serial}")
    def get_by_model_and_serial(
        self,
        model,
        serial
    ):
        """This call will return the telematics resource for the specified model and serial."""

    @returns.json
    @json
    @post("machines/telematics")
    def insert(self, telematics: Body):
        """This call will create telematics information with the specified parameters."""

    @json
    @patch("machines/telematics/{uid}")
    def update(self, uid: str, telematics: Body):
        """This call will update the telematics information with the specified parameters."""

    @delete("machines/telematics/{uid}")
    def delete(self, uid: str):
        """This call will delete the telematics information for the specified uid."""
