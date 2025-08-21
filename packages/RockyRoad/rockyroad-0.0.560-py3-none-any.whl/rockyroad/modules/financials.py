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
class _Financials(Consumer):
    """Inteface to Financials resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    def exchange_rates(self):
        """Inteface to Exchange Rates resource for the RockyRoad API."""
        return self._Exchange_Rates(self)

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class _Exchange_Rates(Consumer):
        """Inteface to exchange rates resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @http_get("financials/exchange-rates")
        def list(
            self,
            date: Query = None

        ):
            """This call will return detailed information for all exchange rates or for those for the specified params."""

        @returns.json
        @http_get("financials/exchange-rates/{date}")
        def get_exchange_rates_by_date(self, date: str):
            """This call will return the specified exchange rates by date."""

        @returns.json
        @http_get("financials/exchange-rates/{uid}")
        def get(self, uid: str):
            """This call will return the specified exchange rates."""

        @delete("financials/exchange-rates/{uid}")
        def delete(self, uid: str):
            """This call will delete the exchange rates for the specified uid."""

        @returns.json
        @json
        @post("financials/exchange-rates")
        def insert(self, exchange_rates: Body):
            """This call will create a exchange rates with the specified parameters."""

        @json
        @patch("financials/exchange-rates/{uid}")
        def update(self, uid: str, exchange_rates: Body):
            """This call will update the exchange rates with the specified parameters."""
