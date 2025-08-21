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
class Parts(Consumer):
    """Inteface to Parts resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    def kits(self):
        return self.__Kits(self)

    @returns.json
    @http_get("parts/reports/parts-backlog")
    def get_parts_backlog(self, company_uid: Query = None, site: Query = None):
        """This call will return the parts backlog report."""

    @returns.json
    @http_get("parts")
    def list(
        self,
        page: Query = None,
        page_size: Query = None,
        uid: Query = None,
        exact_match: Query = None,
        use_or: Query = None,
        partNumber: Query = None,
        partName: Query = None,
        partDescription: Query = None,
        isKit: Query = None,
        isKitPart: Query = None,
        brand: Query = None,
    ):
        """This call will return detailed part information in paginated form for the part(s) specified or all parts if nothing is specified."""

    @returns.json
    @http_get("parts/part-numbers")
    def list_part_numbers(
        self,
        partNumber: Query = None,
        brand: Query = None,
    ):
        """This call will return the part numbers for the part(s) specified."""

    @returns.json
    @http_get("parts/search")
    def parts_searcher(
        self,
        exact_match: Query = None,
        use_or: Query = None,
        partNumber: Query = None,
        partDescription: Query = None,
        brand: Query = None,
    ):
        """This call will return detailed part information for the part(s) specified or all parts if nothing is specified."""

    @returns.json
    @http_get("parts/experimental")
    def list_experimental(
        self,
        uid: Query = None,
        exact_match: Query = None,
        partNumber: Query = None,
        partName: Query = None,
        isKit: Query = None,
        isKitPart: Query = None,
        brand: Query = None,
    ):
        """This call will return detailed part information for the part(s) specified or all parts if nothing is specified."""

    @returns.json
    @http_get("parts/{uid}")
    def get(self, uid: str):
        """This call will get the specified part."""

    @returns.json
    @http_get("parts/{supplier_key}/{part_number}")
    def get_by_supplier_key_and_part_number(self, supplier_key: str, part_number: str):
        """This call will get the specified part."""

    @returns.json
    @http_get("parts/cost/{brand}/{part_number}/date/{date}")
    def get_part_cost(self, brand: str, part_number: str, date: str):
        """This call will get the cost of the specified part."""

    @returns.json
    @http_get("parts/oracle-cost/{brand}/{part_number}/date/{date}")
    def get_oracle_part_cost(self, brand: str, part_number: str, date: str):
        """This call will get the cost of the specified part from Oracle."""

    @returns.json
    @json
    @post("parts")
    def insert(self, part: Body):
        """This call will create a part with the specified parameters."""

    @delete("parts/{uid}")
    def delete(self, uid: str):
        """This call will delete the part for the specified uid."""

    @json
    @patch("parts/{uid}")
    def update(self, uid: str, part: Body):
        """This call will update the part with the specified parameters."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class __Kits(Consumer):
        """Inteface to Kits resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @http_get("parts/kits")
        def list(
            self,
            uid: Query = None,
            kitPartNumber: Query = None,
            partNumber: Query = None,
        ):
            """This call will return detailed kit line item information for the specified uid, kitPartNumber, or partNumber."""

        @returns.json
        @http_get("parts/kits/{uid}")
        def get(self, uid: str):
            """This call will return the kit line item for the specified uid."""

        @delete("parts/kits/{uid}")
        def delete(self, uid: str):
            """This call will delete the kit line item for the specified uid."""

        @returns.json
        @json
        @post("parts/kits")
        def insert(self, kit: Body):
            """This call will create a kit line item with the specified parameters."""

        @json
        @patch("parts/kits/{uid}")
        def update(self, uid: str, kit: Body):
            """This call will update the kit line item with the specified parameters."""
