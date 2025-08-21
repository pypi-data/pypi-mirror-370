from .module_imports import key
from uplink.retry.when import status_5xx
from uplink import (
    get as http_get,
    Consumer,
    returns,
    headers,
    retry,
    Query,
)


@headers({"Ocp-Apim-Subscription-Key": key})
@retry(max_attempts=20, when=status_5xx())
class _Analytics(Consumer):
    """Inteface to API Info resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    @returns.json
    @http_get("analytics/forms/results")
    def form_results(self, form_type: Query = None, form_name: Query = None, model: Query = None, model_group: Query = None, brand: Query = None):
        """Return list of form results"""

    @returns.json
    @http_get("analytics/forms/columns")
    def form_columns(self, form_type: Query = None, form_name: Query = None, model: Query = None, model_group: Query = None, brand: Query = None):
        """Return list of form columns."""

    @returns.json
    @http_get("analytics/forms/supplemental-data")
    def form_supplemental_data_for_analytics(self, supplemental_data_type: Query = None):
        """Return list of form supplemental data."""

    @returns.json
    @http_get("analytics/forms/pdi-model-groups")
    def pdi_model_groups(self):
        """Return list of pdi model groups."""
