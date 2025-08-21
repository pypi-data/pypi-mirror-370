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
class Inspections(Consumer):
    """Inteface to Inspection resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    def reports(self):
        return self.__Reports(self)

    def quotes(self):
        return self.__Quotes(self)

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class __Reports(Consumer):
        """Inteface to Inspection Reports resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @json
        @post("inspections/reports")
        def insert(self, reports: Body):
            """This call will create an inspection report with the specified parameters."""

        @returns.json
        @http_get("inspections/reports")
        def list(
            self,
            company_uid: Query = None,
            uid: Query = None,
            details: Query = None,
            include_deleted: Query = None,
            machine_uid: Query = None,
            inspected_by_user_email: Query = None,

        ):
            """This call will return detailed inspection report information for the specified criteria."""

        @json
        @delete("inspections/reports/{report_uid}")
        def delete(self, report_uid: str):
            """This call will delete the inspection report for the specified uid."""

        @json
        @patch("inspections/reports/restore/{report_uid}")
        def restore(self, report_uid: str):
            """This call will restore the inspection report for the specified uid."""

        @json
        @delete("inspections/reports/temp/{report_uid}")
        def hide(self, report_uid: str):
            """This call will hide the inspection report for the specified uid."""

        @returns.json
        @json
        @patch("inspections/reports")
        def update(self, inspectionReport: Body):
            """This call will update the inspection report with the specified parameters."""

        @json
        @patch("inspections/reports/{report_uid}/field/{field_uid}")
        def update_field(self, report_uid: str, field_uid: str, value: Query):
            """This call will update an inspection report field"""

        @returns.json
        @multipart
        @post("inspections/uploadfiles")
        def addFile(self, uid: Query, file: Part, directory: Query = None):
            """This call will create an inspection report with the specified parameters."""

        @http_get("inspections/download-files")
        def downloadFile(
            self,
            uid: Query,
            filename: Query, directory: Query = None,
        ):
            """This call will download the file associated with the inspection report with the specified uid."""

        @returns.json
        @http_get("inspections/list-files")
        def listFiles(
            self,
            uid: Query, directory: Query = None,
        ):
            """This call will return a list of the files associated with the inspection report for the specified uid."""

        @returns.json
        @http_get("inspections/wear-parts/ranges")
        def listRanges(self, model: Query = None, serial: Query = None):
            """This call will return detailed inspection wear part range information for the specified criteria."""

        @returns.json
        @http_get("inspections/{uid}/parts")
        def listQuoteParts(self, uid: str):
            """This call will return detailed inspection wear part range information for the specified criteria."""

        @returns.json
        @http_get("inspections/fields/mappings")
        def listFields(self, model: Query = None, product_type: Query = None, field: Query = None):
            """This call will return detailed inspection wear part range information for the specified criteria."""

        @returns.json
        @http_get("inspections/fields/mappings/dictionary")
        def listFieldsDictionary(self, model: Query = None, product_type: Query = None, field: Query = None):
            """This call will return detailed inspection wear part range information for the specified criteria."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class __Quotes(Consumer):
        """Inteface to Inspection Quotes for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @http_get("inspections/quotes")
        def list(
            self,
            dealer_uid: Query = None,
            line_items: Query = None,
            include_deleted: Query = None,
            machine_uid: Query = None,

        ):
            """This call will return detailed inspection quote information for the specified criteria."""

        @returns.json
        @http_get("inspections/quotes/{quote_uid}")
        def get(self, quote_uid: str):
            """This call will get an inspection quote by uid"""

        @returns.json
        @json
        @post("inspections/quotes")
        def insert(self, quotes: Body):
            """This call will create an inspection quote with the specified parameters."""

        @json
        @patch("inspections/quotes/{quote_uid}")
        def update(self, quote: Body, quote_uid: str):
            """This call will update the inspection quote with the specified parameters."""

        @json
        @delete("inspections/quotes/{quote_uid}")
        def delete(self, quote_uid: str):
            """This call will delete the inspection quote for the specified uid."""

        @json
        @patch("inspections/quotes/restore/{quote_uid}")
        def restore(self, quote_uid: str):
            """This call will restore the inspection quote for the specified uid."""

        @json
        @delete("inspections/quotes/temp/{quote_uid}")
        def hide(self, quote_uid: str):
            """This call will hide the inspection quote for the specified uid."""
