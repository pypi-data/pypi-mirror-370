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
class Product_Improvements(Consumer):
    """Inteface to Warranties Product Improvement resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    def populations(self):
        return self.Populations(self)

    def machines(self):
        return self.Machines(self)

    def logs(self):
        return self.Logs(self)

    @returns.json
    @http_get("warranties/product-improvements")
    def list(
        self,
        is_published: Query = None,
        pip_type: Query = None,
        pip_status: Query = None,
        show_astec_internal: Query = None,
        show_approved: Query = None,
        brand: Query = None,
    ):
        """This call will return list of product improvements."""

    @delete("warranties/product-improvements/{uid}")
    def delete(self, uid: str):
        """This call will delete the product improvement for the specified uid."""

    @returns.json
    @json
    @post("warranties/product-improvements")
    def insert(self, product_improvement: Body):
        """This call will create the product improvement with the specified parameters."""

    @json
    @patch("warranties/product-improvements/{uid}")
    def update(self, uid: str, product_improvement: Body):
        """This call will update the product improvement with the specified parameters."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class Logs(Consumer):
        """Inteface to Warranties Product Improvement Logs resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            self._base_url = Resource._base_url
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @http_get("warranties/product-improvements/logs")
        def list(self):
            """This call will return list of product improvement logs."""

        @returns.json
        @http_get("warranties/product-improvements/{pip_uid}/logs")
        def list_by_pip(self, pip_uid: str):
            """This call will return list of product improvement logs for the specified product improvement."""

        @returns.json
        @json
        @post("warranties/product-improvements/{pip_uid}/logs")
        def insert(self, pip_uid: str, log: Body):
            """This call will create the product improvement log."""

        @json
        @patch("warranties/product-improvements/logs/{uid}")
        def update(self, uid: str, log: Body):
            """This call will update the product improvement log."""

        @delete("warranties/product-improvements/logs/{uid}")
        def delete(self, uid: str):
            """This call will delete the product improvement log."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class Populations(Consumer):
        """Inteface to Warranties Product Improvement Populations resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            self._base_url = Resource._base_url
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @delete("warranties/product-improvements/populations/{uid}")
        def delete(self, uid: str):
            """This call will delete the population for the specified uid."""

        @returns.json
        @json
        @post("warranties/product-improvements/{pip_uid}/populations")
        def insert(self, pip_uid: str, population: Body):
            """This call will create the population for the specified product improvement."""

        @json
        @patch("warranties/product-improvements/populations/{uid}")
        def update(self, uid: str, population: Body):
            """This call will update the population with the specified parameters."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class Machines(Consumer):
        """Inteface to Warranties PIP machines resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            self._base_url = Resource._base_url
            super().__init__(base_url=Resource._base_url, *args, **kw)

        def logs(self):
            return self.Logs(self)

        @returns.json
        @http_get("warranties/product-improvements/machines")
        def list(
            self,
            machine_uid: Query = None,
            dealer_company_uid: Query = None,
            model: Query = None,
            serial: Query = None,
            pip_uid: Query = None,
            pip_type: Query = None,
            pip_status: Query = None,
            show_astec_internal: Query = None,
            show_approved: Query = None,
            brand: Query = None,
        ):
            """This call will return list of PIP machines."""

        @delete("warranties/product-improvements/machines/{uid}")
        def delete(self, uid: str):
            """This call will the PIP machine."""

        @returns.json
        @json
        @post("warranties/product-improvements/{pip_uid}/machines")
        def insert(self, pip_uid: str, pip_machine: Body):
            """This call will create the PIP machine."""

        @json
        @patch("warranties/product-improvements/machines/{uid}")
        def update(self, uid: str, pip_machine: Body):
            """This call will update the PIP machine."""

        @headers({"Ocp-Apim-Subscription-Key": key})
        @retry(max_attempts=20, when=status_5xx())
        class Logs(Consumer):
            """Inteface to Warranties PIP machines Logs resource for the RockyRoad API."""

            def __init__(self, Resource, *args, **kw):
                self._base_url = Resource._base_url
                super().__init__(base_url=Resource._base_url, *args, **kw)

            @returns.json
            @http_get("warranties/product-improvements/machines/logs")
            def list(self):
                """This call will return list of PIP machines logs."""

            @returns.json
            @http_get("warranties/product-improvements/machines/{pip_machine_uid}/logs")
            def list_by_pip_machine(self, pip_machine_uid: str):
                """This call will return list of PIP machines logs for the specified pip machine."""

            @returns.json
            @json
            @post("warranties/product-improvements/machines/{pip_machine_uid}/logs")
            def insert(self, pip_machine_uid: str, pip_machine_log: Body):
                """This call will create the PIP machine log."""

            @json
            @patch("warranties/product-improvements/machines/logs/{uid}")
            def update(self, uid: str, pip_machine_log: Body):
                """This call will update the PIP machine log."""

            @delete("warranties/product-improvements/machines/logs/{uid}")
            def delete(self, uid: str):
                """This call will delete the PIP machine log."""
