from .module_imports import key
from uplink.retry.when import status_5xx
from uplink import (
    Consumer,
    get as http_get,
    post,
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
class Machine_Passcodes(Consumer):
    """Inteface to machine logs resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    def requests(self):
        """Inteface to Machine Passcode Requests resource for the RockyRoad API."""
        return self._Requests(self)

    @returns.json
    @json
    @post("machine-passcodes/generate")
    def generate(self, machine_passcode_request: Body):
        """This call will generate a new passcode for the specified machine."""

    @returns.json
    @json
    @post("machine-passcodes/verify")
    def verify(self, machine_passcode_request: Body):
        """This call will verify the passcode for the specified machine."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class _Requests(Consumer):
        """Inteface to Machine Passcode Requests resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            self._base_url = Resource._base_url
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @http_get("machine-passcodes/requests")
        def list(self):
            """This call will return a list of machine passcode requests."""

        @returns.json
        @json
        @post("machine-passcodes/requests")
        def insert(self, machine_passcode_request: Body):
            """This call will create a machine passcode request with the specified parameters."""

        @delete("machine-passcodes/requests/{uid}")
        def delete(self, uid: str):
            """This call will delete the machine passcode request for the specified uid."""
