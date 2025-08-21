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
    multipart,
    Part,
)


@headers({"Ocp-Apim-Subscription-Key": key})
@retry(max_attempts=20, when=status_5xx())
class Company_Specified_Info(Consumer):
    """Inteface to Inspection resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    @returns.json
    @json
    @post("companies/specified-info")
    def insert(self, info: Body):
        """This call will create specified info with the specified parameters."""

    @returns.json
    @http_get("companies/specified-info")
    def list(
        self,
        company_uid: Query = None,
        uid: Query = None,
        branch_uid: Query = None,
        has_warranty_rates: Query = None,
        in_active_dealer_listing: Query = None,
        is_inventory_reporting_branch: Query = None,
    ):
        """This call will return specified info for the specified criteria."""

    @returns.json
    @delete("companies/specified-info/{uid}")
    def delete(self, uid: str):
        """This call will delete specified info for the specified uid."""

    @returns.json
    @json
    @patch("companies/specified-info/{uid}")
    def update(self, report: Body, uid: str):
        """This call will update specified info with the specified parameters."""

    @returns.json
    @multipart
    @post("companies/specified-info/upload-files")
    def addFile(self, uid: Query, file: Part):
        """This call will create specified info with the specified parameters."""

    @http_get("companies/specified-info/download-files")
    def downloadFile(
        self,
        uid: Query,
        filename: Query,
    ):
        """This call will download the file associated with the companies/specified-info with the specified uid."""

    @returns.json
    @http_get("companies/specified-info/list-files")
    def listFiles(
        self,
        uid: Query,
    ):
        """This call will return a list of the files associated with the companies/specified-info for the specified uid."""
