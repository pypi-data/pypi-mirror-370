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
class Catalog(Consumer):
    """Inteface to Machine Catalog resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    def aliases(self):
        return self.__Aliases(self)

    @returns.json
    @http_get("machines/catalog")
    def list(self, machine_catalog_uid: Query = None, brand: Query = None, fuzzy_search_term: Query = None, fuzzy_match_limit: Query = None, fuzzy_scorer: Query = None):
        """This call will return detailed machine catalog information for the id specified or all machine catalog information if uid is specified."""

    @returns.json
    @http_get("machines/catalog/v2")
    def list_v2(
        self,
        brand: Query = None,
        uid: Query = None,
        model: Query = None,
        base_model: Query = None,
        product_type: Query = None,
        model_designation: Query = None,
        model_name: Query = None,
        product_description: Query = None,
        official_ms_product_type: Query = None,
        exact_match: Query = False,
    ):
        """This call will return detailed machine catalog information for the specified criteria."""
    
    @returns.json
    @http_get("machines/catalog/{uid}")
    def get(self, uid: str):
        """This call will return detailed machine catalog information for the uid specified."""

    @returns.json
    @json
    @post("machines/catalog")
    def insert(self, new_machine_catalog: Body):
        """This call will create a Machine Catalog entry with the specified parameters."""

    @delete("machines/catalog/{uid}")
    def delete(self, uid: str):
        """This call will delete the Machine Catalog entry for the specified Machine Catalog uid."""

    @json
    @patch("machines/catalog/{uid}")
    def update(self, uid: str, machine_catalog: Body):
        """This call will update the Machine Catalog with the specified parameters."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class __Aliases(Consumer):
        """Inteface to model aliases resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            self._base_url = Resource._base_url
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @http_get("machines/catalog/aliases")
        def list(
            self,
            alias: Query = None,
            brand: Query = None,
            exact_match: Query = None
        ):
            """This call will return detailed information for all aliases."""

        @returns.json
        @http_get("machines/catalog/{machine_catalog_uid}/aliases")
        def list_for(
            self,
            machine_catalog_uid: str,
        ):
            """This call will return aliases for the specified model."""

        @returns.json
        @json
        @post("machines/catalog/{machine_catalog_uid}/aliases")
        def insert(self, machine_catalog_uid: str, alias: Body):
            """This call will create an alias for the specified model."""

        @delete("machines/catalog/aliases/{uid}")
        def delete(self, uid: str):
            """This call will delete the alias for the specified uid."""

        @json
        @patch("machines/catalog/aliases/{uid}")
        def update(self, uid: str, alias: Body):
            """This call will update the alias with the specified parameters."""
