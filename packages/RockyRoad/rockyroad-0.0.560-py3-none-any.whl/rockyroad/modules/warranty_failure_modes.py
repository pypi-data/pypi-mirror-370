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
class Failure_Modes(Consumer):
    """Inteface to Warranties Failure Modes resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    @returns.json
    @http_get("warranties/failure-modes")
    def list(
        self,
        failure_mode_level_1: Query = None,
        cause_type: Query = None
    ):
        """This call will return a list of level 2 failure modes for the specified level 1 failure mode."""
