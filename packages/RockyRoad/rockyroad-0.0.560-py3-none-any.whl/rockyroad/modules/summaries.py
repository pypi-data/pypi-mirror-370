from .module_imports import key
from uplink.retry.when import status_5xx
from uplink import (
    Consumer,
    get as http_get,
    returns,
    headers,
    retry,
    Query,
)


@headers({"Ocp-Apim-Subscription-Key": key})
@retry(max_attempts=20, when=status_5xx())
class Summaries(Consumer):
    """Inteface to Summaries resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    def machineParts(self):
        return self.__Machine_Parts(self)

    def machineOwners(self):
        return self.__Machine_Owners(self)

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class __Machine_Parts(Consumer):
        """Inteface to Machine Parts resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @http_get("summaries/machine-parts")
        def list(
            self,
            machine_uid: Query = None,
            brand: Query = None,
            model: Query = None,
            serial: Query = None,
            account: Query = None,
            account_uid: Query = None,
            dealer_account: Query = None,
            dealer_account_uid: Query = None,
            dealer_uid: Query = None,
            account_association_uid: Query = None,
        ):
            """This call will return detailed summary information of machine parts for the specified search criteria."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class __Machine_Owners(Consumer):
        """Inteface to Machine Owners resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @http_get("summaries/machine-owners")
        def list(
            self,
            model: Query = None,
            serial: Query = None,
            machine_uid: Query = None,
            account: Query = None,
            account_uid: Query = None,
            dealer_account: Query = None,
            dealer_account_uid: Query = None,
            dealer_uid: Query = None,
            account_association_uid: Query = None,
            serial_range_start: Query = None,
            serial_range_stop: Query = 1_000_000,
            engine_hours_last_twelve_months: Query = None,
        ):
            """This call will return detailed summary information of machine owners for the specified serial range and criteria."""
