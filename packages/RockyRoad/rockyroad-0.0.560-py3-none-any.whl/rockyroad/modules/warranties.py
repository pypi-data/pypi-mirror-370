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
    multipart,
    Part,
)


@headers({"Ocp-Apim-Subscription-Key": key})
@retry(max_attempts=20, when=status_5xx())
class Warranties(Consumer):
    """Inteface to Warranties resource for the RockyRoad API."""

    from .warranty_rates import Rates
    from .warranty_registrations import Warranty_Registrations
    from .warranty_failure_modes import Failure_Modes
    from .warranty_gl_codes import GL_Codes
    from .warranty_pip import Product_Improvements
    from .warranty_rga import RGA
    from .warranty_assessments import _Warranty_Assessments
    from .warranty_configurations import _Warranty_Configurations

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    def registrations(self):
        return self.Warranty_Registrations(self)

    def assessments(self):
        return self._Warranty_Assessments(self)

    def creditRequests(self):
        return self.__Credit_Requests(self)

    def rates(self):
        return self.Rates(self)

    def failureModes(self):
        return self.Failure_Modes(self)

    def glCodes(self):
        return self.GL_Codes(self)

    def productImprovements(self):
        return self.Product_Improvements(self)

    def rga(self):
        return self.RGA(self)

    def configurations(self):
        return self._Warranty_Configurations(self)

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class __Credit_Requests(Consumer):
        """Inteface to Warranties Credit Requests resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            self._base_url = Resource._base_url
            super().__init__(base_url=Resource._base_url, *args, **kw)

        def logs(self):
            return self.__Logs(self)

        def analysis(self):
            return self.__Analysis(self)

        def summaries(self):
            return self.__Summaries(self)

        def snapshots(self):
            return self.__Snapshots(self)

        def parts(self):
            return self.__Parts(self)

        @returns.json
        @http_get("warranties/credit-requests")
        def list(
            self,
            uid: Query = None,
            dealer_account: Query = None,
            claimReference: Query = None,
            machine_uid: Query = None,
        ):
            """This call will return detailed warranty credit request information for the specified criteria."""

        @returns.json
        @http_get("warranties/credit-requests/{uid}")
        def get(
            self,
            uid: str,
        ):
            """This call will return detailed warranty credit request information for the specified criteria."""

        @delete("warranties/credit-requests/{uid}")
        def delete(self, uid: str):
            """This call will delete the warranty credit request for the specified uid."""

        @returns.json
        @json
        @post("warranties/credit-requests")
        def insert(self, creditRequest: Body):
            """This call will create a warranty credit request with the specified parameters."""

        @json
        @patch("warranties/credit-requests/{uid}")
        def update(self, uid: str, creditRequest: Body):
            """This call will update the warranty credit request with the specified parameters."""

        @returns.json
        @multipart
        @post("warranties/credit-requests/{uid}/add-files")
        def addFile(self, uid: str, file: Part):
            """This call will a upload file for a warranty credit request with the specified uid."""

        @http_get("warranties/credit-requests/{uid}/download-files")
        def downloadFile(
            self,
            uid: str,
            filename: Query,
        ):
            """This call will download the file associated with the warranty credit request with the specified uid."""

        @returns.json
        @http_get("warranties/credit-requests/{uid}/list-files")
        def listFiles(
            self,
            uid: str,
        ):
            """This call will return a list of the files associated with the warranty credit request for the specified uid."""

        @headers({"Ocp-Apim-Subscription-Key": key})
        @retry(max_attempts=20, when=status_5xx())
        class __Logs(Consumer):
            """Inteface to Warranties Credit Requests Logs resource for the RockyRoad API."""

            def __init__(self, Resource, *args, **kw):
                super().__init__(base_url=Resource._base_url, *args, **kw)

            @returns.json
            @http_get("warranties/credit-requests/logs")
            def list(
                self,
                warranty_credit_request_uid: Query = None,
            ):
                """This call will return log information for the specified criteria."""

            @returns.json
            @http_get("warranties/credit-requests/logs/{uid}")
            def get(self, uid: str):
                """This call will return log information for the specified log uid."""

            @returns.json
            @delete("warranties/credit-requests/logs/{uid}")
            def delete(self, uid: str):
                """This call will delete the log information for the specified uid."""

            @returns.json
            @json
            @post("warranties/credit-requests/logs")
            def insert(self, warranty_log: Body):
                """This call will create log information with the specified parameters."""

            @returns.json
            @json
            @patch("warranties/credit-requests/logs")
            def update(self, log: Body):
                """This call will update the log information with the specified parameters."""

        @headers({"Ocp-Apim-Subscription-Key": key})
        @retry(max_attempts=20, when=status_5xx())
        class __Analysis(Consumer):
            """Inteface to Warranties Credit Requests Analysis resource for the RockyRoad API."""

            def __init__(self, Resource, *args, **kw):
                super().__init__(base_url=Resource._base_url, *args, **kw)

            @returns.json
            @http_get("warranties/credit-requests/analysis")
            def list(
                self,
                include_snapshots: Query = None,
            ):
                """This call will return warranty information for analysis."""

        @headers({"Ocp-Apim-Subscription-Key": key})
        @retry(max_attempts=20, when=status_5xx())
        class __Summaries(Consumer):
            """Inteface to Warranties Credit Requests Summaries resource for the RockyRoad API."""

            def __init__(self, Resource, *args, **kw):
                super().__init__(base_url=Resource._base_url, *args, **kw)

            @returns.json
            @http_get("warranties/credit-requests/summaries")
            def list(
                self,
                dealer_account: Query = None,
                dealer_code: Query = None,
                dealer_uid: Query = None,
                machine_uid: Query = None,
                is_active: Query = None,
            ):
                """This call will return a summary of warranty information."""

            @returns.json
            @http_get("warranties/credit-requests/summaries/{uid}")
            def get(
                self,
                uid: str,
            ):
                """This call will return a summary for the specified warranty credit request."""

        @headers({"Ocp-Apim-Subscription-Key": key})
        @retry(max_attempts=20, when=status_5xx())
        class __Snapshots(Consumer):
            """Inteface to Warranties Credit Requests Snapshots resource for the RockyRoad API."""

            def __init__(self, Resource, *args, **kw):
                super().__init__(base_url=Resource._base_url, *args, **kw)

            @returns.json
            @http_get(
                "warranties/credit-requests/{warranty_credit_request_uid}/snapshots"
            )
            def list(
                self,
                warranty_credit_request_uid: str,
            ):
                """This call will return snapshot information for the specified criteria."""

        @headers({"Ocp-Apim-Subscription-Key": key})
        @retry(max_attempts=20, when=status_5xx())
        class __Parts(Consumer):
            """Inteface to Warranty Parts resource for the RockyRoad API."""

            def __init__(self, Resource, *args, **kw):
                self._base_url = Resource._base_url
                super().__init__(base_url=Resource._base_url, *args, **kw)

            @json
            @patch("warranties/credit-requests/parts/{uid}")
            def update(self, uid: str, warranty_part: Body):
                """This call will update the warranty part with the specified parameters."""
