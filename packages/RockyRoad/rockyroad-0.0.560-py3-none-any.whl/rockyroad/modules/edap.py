from .module_imports import get_key
from uplink.retry.when import status_5xx
from uplink import (
    Consumer,
    get as http_get,
    returns,
    headers,
    retry,
    Query,
    Path,
)

# Module configuration
USE_SERVICES_API = True
key = get_key(use_services_api=USE_SERVICES_API)

@headers({"Ocp-Apim-Subscription-Key": key})
@retry(max_attempts=20, when=status_5xx())
class EDAP(Consumer):
    """Inteface to EDAP resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._services_base_url if USE_SERVICES_API else Resource._base_url
        super().__init__(base_url=self._base_url, *args, **kw)

    def asset_sales(self):
        return self.__Asset_Sales(self)

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class __Asset_Sales(Consumer):
        """Inteface to EDAP Sales resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            self._base_url = Resource._base_url
            super().__init__(base_url=self._base_url, *args, **kw)

        @returns.json
        @http_get("edap/sales")
        def list(
            self,
            business_unit_id: Query = None,
            model: Query = None,
            serial_number: Query = None,
        ):
            """This call will return EDAP asset sales information for the specified criteria."""

        @returns.json
        @http_get("edap/sales-orders/sites/{site}/categories/{category}")
        def list_by_category_and_site(
            self,
            site: Path = None,
            category: Path = None,
        ):
            """This call will return EDAP sales orders for the specified category and site."""
