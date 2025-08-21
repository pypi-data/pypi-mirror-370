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
class _TCO(Consumer):
    """Inteface to TCO resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    def costModel(self):
        return self._Cost_Model(self)

    def maintenance(self):
        return self._Maintenance(self)

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class _Cost_Model(Consumer):
        """Inteface to TCO Cost Model resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            self._base_url = Resource._base_url
            super().__init__(base_url=Resource._base_url, *args, **kw)

        def machines(self):
            return self._Machines(self)

        @returns.json
        @http_get("calculators/tco/cost-model")
        def list(
                self, is_validated: Query = None, is_maintenance_calculator: Query = None):
            """This call will return list of TCO Cost Model."""

        @returns.json
        @http_get("calculators/tco/cost-model/{uid}")
        def get(self, uid: str):
            """This call will return the specified TCO Cost Model."""

        @delete("calculators/tco/cost-model/{uid}")
        def delete(self, uid: str):
            """This call will delete the TCO Cost Model."""

        @returns.json
        @json
        @post("calculators/tco/cost-model")
        def insert(self, tco_part: Body):
            """This call will create the TCO Cost Model."""

        @json
        @patch("calculators/tco/cost-model/{uid}")
        def update(self, uid: str, tco_part: Body):
            """This call will update the TCO Cost Model."""

        @headers({"Ocp-Apim-Subscription-Key": key})
        @retry(max_attempts=20, when=status_5xx())
        class _Machines(Consumer):
            """Inteface to TCO models resource for the RockyRoad API."""

            def __init__(self, Resource, *args, **kw):
                self._base_url = Resource._base_url
                super().__init__(base_url=Resource._base_url, *args, **kw)

            def catalogs(self):
                return self._Catalogs(self)

            @headers({"Ocp-Apim-Subscription-Key": key})
            @retry(max_attempts=20, when=status_5xx())
            class _Catalogs(Consumer):
                """Inteface to TCO models resource for the RockyRoad API."""

                def __init__(self, Resource, *args, **kw):
                    self._base_url = Resource._base_url
                    super().__init__(base_url=Resource._base_url, *args, **kw)

                @returns.json
                @http_get("calculators/tco/cost-model/machines/catalogs/{uid}")
                def get(self, uid: str):
                    """This call will return the TCO cost model for the specified machine catalog uid."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class _Maintenance(Consumer):
        """Inteface to TCO resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            self._base_url = Resource._base_url
            super().__init__(base_url=Resource._base_url, *args, **kw)

        def parts(self):
            return self._Parts(self)

        @returns.json
        @http_get("calculators/tco/maintenance")
        def list(
            self, machine_catalog_uid: Query = None,
        ):
            """This call will return list of TCO Maintenances."""

        @returns.json
        @http_get("calculators/tco/maintenance/{uid}")
        def get(self, uid: str):
            """This call will return the specified TCO Maintenance."""

        @delete("calculators/tco/maintenance/{uid}")
        def delete(self, uid: str):
            """This call will delete the TCO Maintenance."""

        @returns.json
        @json
        @post("calculators/tco/maintenance")
        def insert(self, tco_part: Body):
            """This call will create the TCO Maintenance."""

        @json
        @patch("calculators/tco/maintenance/{uid}")
        def update(self, uid: str, tco_part: Body):
            """This call will update the TCO Maintenance."""

        @headers({"Ocp-Apim-Subscription-Key": key})
        @retry(max_attempts=20, when=status_5xx())
        class _Parts(Consumer):
            """Inteface to TCO resource for the RockyRoad API."""

            def __init__(self, Resource, *args, **kw):
                self._base_url = Resource._base_url
                super().__init__(base_url=Resource._base_url, *args, **kw)

            def parts(self):
                return self.TCO(self)

            @returns.json
            @http_get("calculators/tco/maintenance/parts")
            def list(
                self,
            ):
                """This call will return list of TCO Parts."""

            @returns.json
            @http_get("calculators/tco/maintenance/parts/{uid}")
            def get(self, uid: str):
                """This call will return the specified TCO Part."""

            @delete("calculators/tco/maintenance/parts/{uid}")
            def delete(self, uid: str):
                """This call will delete the TCO Part."""

            @returns.json
            @json
            @post("calculators/tco/maintenance/parts")
            def insert(self, tco_part: Body):
                """This call will create the TCO Part."""

            @json
            @patch("calculators/tco/maintenance/parts/{uid}")
            def update(self, uid: str, tco_part: Body):
                """This call will update the TCO Part."""
