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
class Apbs(Consumer):
    """Inteface to APBs resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    def status(self):
        return self.__Status(self)

    def requests(self):
        return self.__Requests(self)

    @returns.json
    @http_get("apbs")
    def list(
        self,
        apb_uid: Query = None,
        account: Query = None,
        list_apbs_for_dealer_supported_accounts: Query = None,
        list_apbs_for_dealer_supported_machines: Query = None,
        brand: Query = None,
        model: Query = None,
        serial: Query = None,
        branch_uid: Query = None,
        dealer_code: Query = None,
        dealer_uid: Query = None,
        dealer_branch_uid: Query = None,
    ):
        """This call will return detailed APB information for the apb or machine specified or all APBs if nothing is specified."""

    @returns.json
    @json
    @post("apbs")
    def insert(self, new_apb: Body):
        """This call will create an APB with the specified parameters."""

    @returns.json
    @delete("apbs")
    def delete(self, apb_uid: Query):
        """This call will delete the APB for the specified APB uid."""

    @returns.json
    @json
    @patch("apbs")
    def update(self, apb: Body):
        """This call will update the APB with the specified parameters."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class __Status(Consumer):
        """Inteface to APB Status resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @http_get("apbs/status")
        def list(self, apb_uid: Query = None):
            """This call will return detailed APB status information for the specified APB uid."""

        @returns.json
        @delete("apbs/status")
        def delete(self, apb_status_uid: Query):
            """This call will delete the APB Status for the specified APB uid and APB Status uid."""

        @returns.json
        @json
        @post("apbs/status")
        def insert(self, new_apb_status: Body):
            """This call will create an alert request with the specified parameters."""

        @returns.json
        @json
        @patch("apbs/status")
        def update(self, apb_status: Body):
            """This call will update the APB status with the specified parameters."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class __Requests(Consumer):
        """Inteface to APB Request resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @http_get("apbs/requests")
        def list(self, uid: Query = None):
            """This call will return detailed information for APB requests for the specified APB Request uid."""

        @returns.json
        @http_get("apbs/requests/{uid}")
        def get(self, uid: str):
            """This call will return detailed information for the specified APB request."""

        @returns.json
        @delete("apbs/requests")
        def delete(self, uid: Query):
            """This call will delete the APB Request for the specified APB Request uid."""

        @returns.json
        @json
        @post("apbs/requests")
        def insert(self, new_apb_request: Body):
            """This call will create an APB request with the specified parameters."""

        @returns.json
        @json
        @patch("apbs/requests")
        def update(self, apb_request: Body):
            """This call will update the APB Request with the specified parameters."""
