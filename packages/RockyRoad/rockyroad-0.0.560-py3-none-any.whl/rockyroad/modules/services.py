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
class Services(Consumer):
    """Inteface to Services resource for the RockyRoad API."""

    from .service_reports import Service_Reports

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    def maintenanceIntervals(self):
        return self.__Maintenance_Intervals(self)

    def emails(self):
        return self.__Emails(self)

    def templates(self):
        return self.__Templates(self)

    def serviceReports(self):
        return self.Service_Reports(self)

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class __Maintenance_Intervals(Consumer):
        """Inteface to Maintenance Intervals resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @http_get("services/maintenance-intervals")
        def list(
            self,
            uid: Query = None,
            machine_catalog_uid: Query = None,
            hours: Query = None,
            brand: Query = None,
            model: Query = None,
            serial: Query = None,
            is_tco: Query = None
        ):
            """This call will return detailed information for all maintenance intervals or for those for the specified uid, hours, or brand and model."""

        @returns.json
        @http_get("services/maintenance-intervals/{uid}")
        def get(self, uid: str):
            """This call will return the specified maintenance interval."""

        @delete("services/maintenance-intervals/{uid}")
        def delete(self, uid: str):
            """This call will delete the maintenance interval for the specified uid."""

        @returns.json
        @json
        @post("services/maintenance-intervals")
        def insert(self, maintenance_interval: Body):
            """This call will create a maintenance interval with the specified parameters."""

        @json
        @patch("services/maintenance-intervals/{uid}")
        def update(self, uid: str, maintenance_interval: Body):
            """This call will update the maintenance interval with the specified parameters."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class __Emails(Consumer):
        """Inteface to Warranty Emails resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            self._base_url = Resource._base_url
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @json
        @post("services/emails/reset-service-due-hours")
        def resetServiceDueHours(
            self, email_fields: Body, useLocalTemplate: Query = None
        ):
            """This call will create a service request email from a template with the specified parameters."""

        @json
        @post("services/emails")
        def create(
            self,
            email_template: Query,
            email_fields: Body,
            useLocalTemplate: Query = None,
        ):
            """This call will create a service request email from a template with the specified parameters."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class __Templates(Consumer):
        """Inteface to Templates resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            self._base_url = Resource._base_url
            super().__init__(base_url=Resource._base_url, *args, **kw)

        def emails(self):
            return self.__Emails(self)

        def documents(self):
            return self.__Documents(self)

        def pdfs(self):
            return self.__Pdfs(self)

        @headers({"Ocp-Apim-Subscription-Key": key})
        @retry(max_attempts=20, when=status_5xx())
        class __Emails(Consumer):
            """Inteface to Email Templates resource for the RockyRoad API."""

            def __init__(self, Resource, *args, **kw):
                self._base_url = Resource._base_url
                super().__init__(base_url=Resource._base_url, *args, **kw)

            @json
            @post("services/templates/emails")
            def create(
                self,
                email_template: Query,
                email_fields: Body,
            ):
                """This call will create html email content from a template with the specified parameters."""

        @headers({"Ocp-Apim-Subscription-Key": key})
        @retry(max_attempts=20, when=status_5xx())
        class __Documents(Consumer):
            """Inteface to Documents Templates resource for the RockyRoad API."""

            def __init__(self, Resource, *args, **kw):
                self._base_url = Resource._base_url
                super().__init__(base_url=Resource._base_url, *args, **kw)

            @json
            @post("services/templates/documents")
            def create(
                self,
                document_template: Query,
                document_fields: Body,
            ):
                """This call will create html document content from a template with the specified parameters."""

        @headers({"Ocp-Apim-Subscription-Key": key})
        @retry(max_attempts=20, when=status_5xx())
        class __Pdfs(Consumer):
            """Inteface to PDF Templates resource for the RockyRoad API."""

            def __init__(self, Resource, *args, **kw):
                self._base_url = Resource._base_url
                super().__init__(base_url=Resource._base_url, *args, **kw)

            @json
            @post("services/templates/pdfs")
            def create(
                self,
                pdf_params: Body,
                document_template: Query = None,
                include_page_numbers: Query = False,
                orientation: Query = "portrait",
            ):
                """This call will create html document content from a template with the specified parameters."""
