from .module_imports import key
from uplink.retry.when import status_5xx
from uplink import (
    Consumer,
    get as http_get,
    post,
    patch,
    returns,
    headers,
    retry,
    Query,
)


@headers({"Ocp-Apim-Subscription-Key": key})
@retry(max_attempts=20, when=status_5xx())
class _Oracle_Installed_Base_Assets(Consumer):
    """Inteface to Oracle knowledge management resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    @returns.json
    @http_get("oracle/installed-base-assets")
    def list(
        self,
        expand: Query = None,
        fields: Query = None,
        finder: Query = None,
        limit: Query = None,
        links: Query = None,
        offset: Query = None,
        only_data: Query = None,
        order_by: Query = None,
        q: Query = None,
        total_results: Query = None,
    ):
        """This call will return installed base assets from Oracle."""

    @returns.json
    @http_get("oracle/installed-base-assets/{asset_id}")
    def get(
        self,
        asset_id: int,
        expand: Query = None,
        fields: Query = None,
        links: Query = None,
        only_data: Query = None,
    ):
        """Return the installed base asset from Oracle."""

    @returns.json
    @post("oracle/installed-base-assets/machines")
    def insert_machines_from_oracle(
        self,
        start_shipment_date: Query,
        operating_organization_name: Query,
        end_shipment_date: Query = None,
    ):
        """Create new machines based on Oracle installed base assets."""

    @returns.json
    @post("oracle/installed-base-assets/legacy-machines")
    def insert_legacy_machines_from_oracle(
        self,
        start_shipment_date: Query,
        operating_organization_name: Query,
        end_shipment_date: Query = None,
    ):
        """Create new machines based on Oracle installed base assets."""

    @returns.json
    @patch("oracle/installed-base-assets/legacy-machines")
    def update_legacy_machines_from_oracle(
        self,
        start_shipment_date: Query,
        operating_organization_name: Query,
        end_shipment_date: Query = None,
    ):
        """Update existing machines based on Oracle installed base assets."""

    @patch("oracle/installed-base-assets/startup-date")
    def update_startup_date_from_oracle(
        self,
        start_shipment_date: Query = None,
        operating_organization_name: Query = None,
        end_shipment_date: Query = None,
    ):
        """Update startup date based on Oracle installed base assets."""
