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
class RGA(Consumer):
    """Inteface to Warranties RGA resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    def parts(self):
        return self.Parts(self)

    def shipments(self):
        return self.Shipments(self)

    @returns.json
    @http_get("warranties/rga/shipping-accounts")
    def list_shipper_accounts(self):
        """This call will return a dictionary of RGA shipping accounts."""

    @returns.json
    @http_get("warranties/rga")
    def list(self, company_uid: Query = None, rga_number: Query = None, machine_uid: Query = None):
        """This call will return list of RGAs."""

    @returns.json
    @http_get("warranties/rga/{uid}")
    def get(self, uid: str):
        """This call will get the RGA for the specified uid."""

    @delete("warranties/rga/{uid}")
    def delete(self, uid: str):
        """This call will delete the RGA for the specified uid."""

    @returns.json
    @json
    @post("warranties/rga")
    def insert(self, rga: Body):
        """This call will create the RGA with the specified parameters."""

    @json
    @patch("warranties/rga/{uid}")
    def update(self, uid: str, rga: Body):
        """This call will update the RGA with the specified parameters."""

    @json
    @post("warranties/rga/{uid}/email")
    def send_notification(self, uid: str, options: Body = None):
        """This call will send an email notification for the specified RGA to the subscribed recipient or to optional recipients as provided."""

    @json
    @post("warranties/rga/{uid}/email-status-update")
    def send_status_update_notification(self, uid: str, options: Body = None):
        """This call will send an email status update notification for the specified RGA to the subscribed recipient or to optional recipients as provided."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class Parts(Consumer):
        """Inteface to Warranties RGA parts resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            self._base_url = Resource._base_url
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @http_get("warranties/rga/{rga_uid}/parts")
        def list(self, rga_uid: str):
            """This call will return list of RGA parts."""

        @delete("warranties/rga/parts/{uid}")
        def delete(self, uid: str):
            """This call will the RGA part."""

        @returns.json
        @json
        @post("warranties/rga/{rga_uid}/parts")
        def insert(self, rga_uid: str, rga_part: Body):
            """This call will create the RGA part."""

        @json
        @patch("warranties/rga/parts/{uid}")
        def update(self, uid: str, rga_part: Body):
            """This call will update the RGA part."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class Shipments(Consumer):
        """Inteface to Warranties RGA Shipments resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            self._base_url = Resource._base_url
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @http_get("warranties/rga/shipments")
        def list(self):
            """This call will return list of RGA shipments."""

        @returns.json
        @http_get("warranties/rga/{rga_uid}/shipments")
        def list_for_rga(self, rga_uid: str):
            """This call will return list of RGA shipments."""

        @returns.json
        @http_get("warranties/rga/shipments/{uid}")
        def get(self, uid: str):
            """This call will return the RGA shipment for the specified uid."""

        @delete("warranties/rga/shipments/{uid}")
        def delete(self, uid: str):
            """This call will the RGA shipment."""

        @returns.json
        @json
        @post("warranties/rga/{rga_uid}/shipments")
        def insert(self, rga_uid: str, rga_part: Body):
            """This call will create the RGA shipment."""

        @json
        @patch("warranties/rga/shipments/{uid}")
        def update(self, uid: str, rga_part: Body):
            """This call will update the RGA shipment."""
