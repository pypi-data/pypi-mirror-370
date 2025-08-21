from .module_imports import get_key
from uplink.retry.when import status_5xx
from uplink import (
    Consumer,
    delete,
    get as http_get,
    patch,
    post,
    json,
    returns,
    headers,
    retry,
    Body,
    Query,
    Path,
    multipart,
    Part,
)

# Module configuration
USE_SERVICES_API = True
key = get_key(use_services_api=USE_SERVICES_API)


@headers({"Ocp-Apim-Subscription-Key": key})
@retry(max_attempts=20, when=status_5xx())
class Documoto(Consumer):
    """Interface to Documoto resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._services_base_url if USE_SERVICES_API else Resource._base_url
        super().__init__(base_url=self._base_url, *args, **kw)

    def files(self):
        return self.__Files(self)

    def order_logs(self):
        return self.__Order_Logs(self)

    def search_logs(self):
        return self.__Search_Logs(self)

    def user_action_logs(self):
        return self.__User_Action_Logs(self)

    def login_logs(self):
        return self.__Login_Logs(self)

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class __Files(Consumer):
        """Interface to Technical Content Feedback Entries resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            self._base_url = Resource._base_url
            super().__init__(base_url=self._base_url, *args, **kw)

        @returns.json
        @http_get("documoto/files")
        def list_files(self):
            """This call will return a list of available documoto files."""

        @returns.json
        @http_get("documoto/latest-daily-link")
        def get_latest_daily_link(self):
            """This call will return the latest daily link for documoto files."""

        @returns.json
        @http_get("documoto/generate-link")
        def generate_link(self, filename: Query):
            """This call will generate a download link for the specified filename."""

        # CSV Log Processing
        @multipart
        @post("documoto/logs/type/{log_type}")
        def process_csv_logs(
            self,
            csv_file: Part,
            log_type: Path,  # orders_log, search_log, or user_action_log
            created_by: Query
        ):
            """This call will process and upload a CSV file for the specified log type."""


        @post("documoto/logs/type/{log_type}/date/{date}")
        def insert_logs_by_date(self, log_type: Path, date: Path, created_by: Query):
            """This call will insert logs for the specified log type and date."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class __Order_Logs(Consumer):
        """Interface to Technical Content Feedback Entries resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            self._base_url = Resource._base_url
            super().__init__(base_url=self._base_url, *args, **kw)

        @returns.json
        @http_get("documoto/logs/orders")
        def list(self):
            """This call will return all orders logs."""

        @returns.json
        @http_get("documoto/logs/orders/{log_uid}")
        def get(self, log_uid: Path):
            """This call will return a specific orders log by its UID."""
        
        @json
        @patch("documoto/logs/orders/{log_uid}")
        def update(self, log_uid: Path, update_data: Body):
            """This call will update a specific orders log by its UID."""

        @delete("documoto/logs/orders/{log_uid}")
        def delete(self, log_uid: Path):
            """This call will delete a specific orders log by its UID."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class __Search_Logs(Consumer):
        """Interface to Technical Content Feedback Entries resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            self._base_url = Resource._base_url
            super().__init__(base_url=self._base_url, *args, **kw)

        @returns.json
        @http_get("documoto/logs/search")
        def list(self):
            """This call will return all search logs."""

        @returns.json
        @http_get("documoto/logs/search/{log_uid}")
        def get(self, log_uid: Path):
            """This call will return a specific search log by its UID."""

        @json
        @patch("documoto/logs/search/{log_uid}")
        def update(self, log_uid: Path, update_data: Body):
            """This call will update a specific search log by its UID."""

        @delete("documoto/logs/search/{log_uid}")
        def delete(self, log_uid: Path):
            """This call will delete a specific search log by its UID."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class __User_Action_Logs(Consumer):
        """Interface to Technical Content Feedback Entries resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            self._base_url = Resource._base_url
            super().__init__(base_url=self._base_url, *args, **kw)

        @returns.json
        @http_get("documoto/logs/user_action")
        def list(self):
            """This call will return all user action logs."""

        @returns.json
        @http_get("documoto/logs/user_action/{log_uid}")
        def get(self, log_uid: Path):
            """This call will return a specific user action log by its UID."""

        @json
        @patch("documoto/logs/user_action/{log_uid}")
        def update(self, log_uid: Path, update_data: Body):
            """This call will update a specific user action log by its UID."""

        @delete("documoto/logs/user_action/{log_uid}")
        def delete(self, log_uid: Path):
            """This call will delete a specific user action log by its UID."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class __Login_Logs(Consumer):
        """Interface to Technical Content Feedback Entries resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            self._base_url = Resource._base_url
            super().__init__(base_url=self._base_url, *args, **kw)

        @returns.json
        @http_get("documoto/logs/login")
        def list(self):
            """This call will return all login logs."""

        @returns.json
        @http_get("documoto/logs/login/{log_uid}")
        def get(self, log_uid: Path):
            """This call will return a specific login log by its UID."""

        @json
        @patch("documoto/logs/login/{log_uid}")
        def update(self, log_uid: Path, update_data: Body):
            """This call will update a specific login log by its UID."""

        @delete("documoto/logs/login/{log_uid}")
        def delete(self, log_uid: Path):
            """This call will delete a specific login log by its UID."""
    