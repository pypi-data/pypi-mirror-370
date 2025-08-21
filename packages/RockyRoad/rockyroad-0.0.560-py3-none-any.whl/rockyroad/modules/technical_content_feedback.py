from .module_imports import get_key
from uplink.retry.when import status_5xx
from uplink import (
    Consumer,
    Path,
    delete,
    get as http_get,
    patch,
    post,
    returns,
    headers,
    retry,
    Body,
    json,
    Query,
)

# Module configuration
USE_SERVICES_API = True
key = get_key(use_services_api=USE_SERVICES_API)


@headers({"Ocp-Apim-Subscription-Key": key})
@retry(max_attempts=20, when=status_5xx())
class Technical_Content_Feedback(Consumer):
    """Interface to Technical Content Feedback resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._services_base_url if USE_SERVICES_API else Resource._base_url
        super().__init__(base_url=self._base_url, *args, **kw)

    def entries(self):
        return self.__Entries(self)

    def productGroups(self):
        return self.__Product_Groups(self)

    def productLines(self):
        return self.__Product_Lines(self)

    def contentTypes(self):
        return self.__Content_Types(self)

    def users(self):
        return self.__Users(self)

    def assignments(self):
        return self.__Assignments(self)

    def comments(self):
        return self.__Comments(self)

    def logs(self):
        return self.__Logs(self)

    def emails(self):
        return self.__Emails(self)

    def documents(self):
        return self.__Documents(self)

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class __Entries(Consumer):
        """Interface to Technical Content Feedback Entries resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            self._base_url = Resource._base_url
            super().__init__(base_url=self._base_url, *args, **kw)

        @returns.json
        @http_get("technical-content-feedback/entries")
        def list(
            self,
            status: Query = None,
            priority: Query = None,
            product_group_uid: Query = None,
            brand_uid: Query = None,
            product_line_uid: Query = None,
            content_type_uid: Query = None,
            user_uid: Query = None,
            company_uid: Query = None,
            machine_uid: Query = None,
        ):
            """This call will return detailed technical content feedback information for the specified criteria."""

        @returns.json
        @http_get("technical-content-feedback/entries/{uid}")
        def get(
            self,
            uid: str,
        ):
            """This call will return detailed technical content feedback information for the specified criteria."""

        @delete("technical-content-feedback/entries/{uid}")
        def delete(self, uid: str):
            """This call will delete the technical content feedback for the specified uid."""

        @returns.json
        @json
        @post("technical-content-feedback/entries")
        def insert(self, entry: Body):
            """This call will create a technical content feedback with the specified parameters."""

        @json
        @patch("technical-content-feedback/entries/{uid}")
        def update(self, uid: str, entry: Body):
            """This call will update the technical content feedback with the specified parameters."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class __Comments(Consumer):
        """Interface to Technical Content Feedback Comments resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            self._base_url = Resource._base_url
            super().__init__(base_url=self._base_url, *args, **kw)

        @returns.json
        @http_get("technical-content-feedback/comments")
        def list(self):
            """This call will return list of comments."""

        @returns.json
        @http_get("technical-content-feedback/comments/{uid}")
        def get(self, uid: str):
            """This call will return a comment for the specified uid."""

        @returns.json
        @http_get("technical-content-feedback/entries/{entry_uid}/comments")
        def list_by_entry(self, entry_uid: str):
            """This call will return list of comments for the specified entry uid."""

        @returns.json
        @json
        @post("technical-content-feedback/entries/{entry_uid}/comments")
        def insert(self, entry_uid: str, comment: Body):
            """This call will create a comment with the specified parameters."""

        @json
        @patch("technical-content-feedback/comments/{uid}")
        def update(self, uid: str, comment: Body):
            """This call will update the comment with the specified parameters."""

        @delete("technical-content-feedback/comments/{uid}")
        def delete(self, uid: str):
            """This call will delete the comment for the specified uid."""


    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class __Logs(Consumer):
        """Interface to Technical Content Feedback Logs resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            self._base_url = Resource._base_url
            super().__init__(base_url=self._base_url, *args, **kw)

        @returns.json
        @http_get("technical-content-feedback/logs")
        def list(
            self,
            log_type: Query = None,
        ):
            """This call will return a list of log information."""

        @returns.json
        @json
        @post("technical-content-feedback/logs/")
        def insert(self, log: Body):
            """This call will create log information with the specified parameters."""

        @returns.json
        @http_get("technical-content-feedback/logs/{log_uid}")
        def get(self, log_uid: str):
            """This call will return log information for the specified log uid."""

        @delete("technical-content-feedback/logs/{log_uid}")
        def delete(self, log_uid: str):
            """This call will delete the log information for the specified log uid."""

        @json
        @patch("technical-content-feedback/logs/{log_uid}")
        def update(self, log_uid: str, log: Body):
            """This call will update the log information with the specified parameters."""

        @returns.json
        @http_get("technical-content-feedback/entries/{entry_uid}/logs")
        def list_by_entry(
            self,
            entry_uid: str,
            log_type: Query = None,
        ):
            """This call will return log information for the specified entry uid."""

        @returns.json
        @json
        @post("technical-content-feedback/entries/{entry_uid}/logs")
        def insert_by_entry(self, entry_uid: str, log: Body):
            """This call will create log information with the specified parameters."""

        @returns.json
        @http_get("technical-content-feedback/product-groups/{product_group_uid}/logs")
        def list_by_product_group(self, product_group_uid: str, log_type: Query = None):
            """This call will return log information for the specified product group uid."""

        @returns.json
        @json
        @post("technical-content-feedback/product-groups/{product_group_uid}/logs")
        def insert_by_product_group(self, product_group_uid: str, log: Body):
            """This call will create log information with the specified parameters."""
    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class __Emails(Consumer):
        """Interface to Technical Content Feedback Emails resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            self._base_url = Resource._base_url
            super().__init__(base_url=self._base_url, *args, **kw)

        @returns.json
        @http_get("technical-content-feedback/emails")
        def list(self):
            """This call will return a list of emails."""

        @returns.json
        @http_get("technical-content-feedback/entries/{entry_uid}/emails")
        def list_by_entry(self, entry_uid: str):
            """This call will return a list of emails for the specified entry uid."""

        @returns.json
        @http_get("technical-content-feedback/emails/{uid}")
        def get(self, uid: str):
            """This call will return an email for the specified uid."""

        @returns.json
        @json
        @post("technical-content-feedback/emails")
        def insert(self, email: Body):
            """This call will create an email with the specified parameters."""

        @json
        @patch("technical-content-feedback/emails/{uid}")
        def update(self, uid: str, email: Body):
            """This call will update the email with the specified parameters."""

        @delete("technical-content-feedback/emails/{uid}")
        def delete(self, uid: str):
            """This call will delete the email for the specified uid."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class __Product_Groups(Consumer):
        """Interface to Technical Content Feedback Product Groups resource for the RockyRoad API."""
        
        def __init__(self, Resource, *args, **kw):
            self._base_url = Resource._base_url
            super().__init__(base_url=self._base_url, *args, **kw)
        
        @returns.json
        @http_get("technical-content-feedback/product-groups")
        def list(self):
            """This call will return a list of product groups."""
        
        @returns.json
        @http_get("technical-content-feedback/product-groups/{uid}")
        def get(self, uid: str):
            """This call will return a product group for the specified uid."""
        
        @returns.json
        @json
        @post("technical-content-feedback/product-groups")
        def insert(self, product_group: Body):
            """This call will create a product group with the specified parameters."""
        
        @json
        @patch("technical-content-feedback/product-groups/{uid}")
        def update(self, uid: str, product_group: Body):
            """This call will update the product group with the specified parameters."""
        
        @delete("technical-content-feedback/product-groups/{uid}")
        def delete(self, uid: str):
            """This call will delete the product group for the specified uid."""



    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class __Product_Lines(Consumer):
        """Interface to Technical Content Feedback Product Lines resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            self._base_url = Resource._base_url
            super().__init__(base_url=self._base_url, *args, **kw)

        @returns.json
        @http_get("technical-content-feedback/product-lines")
        def list(self,
            name: Query = None,
            product_group_uid: Query = None,
            brand_uid: Query = None,
            ):
            """This call will return a list of product lines."""
        
        @returns.json
        @http_get("technical-content-feedback/product-lines/{uid}")
        def get(self, uid: str):
            """This call will return a product line for the specified uid."""
        
        @returns.json
        @json
        @post("technical-content-feedback/product-lines")
        def insert(self, product_line: Body):
            """This call will create a product line with the specified parameters."""
        
        @json
        @patch("technical-content-feedback/product-lines/{uid}")
        def update(self, uid: str, product_line: Body):
            """This call will update the product line with the specified parameters."""
        
        @delete("technical-content-feedback/product-lines/{uid}")
        def delete(self, uid: str):
            """This call will delete the product line for the specified uid."""

    

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class __Content_Types(Consumer):
        """Interface to Technical Content Feedback Content Types resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            self._base_url = Resource._base_url
            super().__init__(base_url=self._base_url, *args, **kw)

        @returns.json
        @http_get("technical-content-feedback/content-types")
        def list(self):
            """This call will return a list of content types."""
        
        @returns.json
        @http_get("technical-content-feedback/content-types/{uid}")
        def get(self, uid: str):
            """This call will return a content type for the specified uid."""
        
        @returns.json
        @json
        @post("technical-content-feedback/content-types")
        def insert(self, content_type: Body):
            """This call will create a content type with the specified parameters."""
        
        @json
        @patch("technical-content-feedback/content-types/{uid}")
        def update(self, uid: str, content_type: Body):
            """This call will update the content type with the specified parameters."""
        
        @delete("technical-content-feedback/content-types/{uid}")
        def delete(self, uid: str):
            """This call will delete the content type for the specified uid."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class __Documents(Consumer):
        """Interface to Technical Content Feedback Documents resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            self._base_url = Resource._base_url
            super().__init__(base_url=self._base_url, *args, **kw)

        @returns.json
        @http_get("technical-content-feedback/documents")
        def list(
            self,
            category: Query = None,
            sub_category: Query = None,
            name: Query = None,
            exact_match: Query = None,
            ):
            """This call will return a list of documents."""
        
        @returns.json
        @http_get("technical-content-feedback/documents/{uid}")
        def get(self, uid: str):
            """This call will return a document for the specified uid."""
        
        @returns.json
        @json
        @post("technical-content-feedback/documents")
        def insert(self, document: Body):
            """This call will create a document with the specified parameters."""
        
        @json
        @patch("technical-content-feedback/documents/{uid}")
        def update(self, uid: str, document: Body):
            """This call will update the document with the specified parameters."""
        
        @delete("technical-content-feedback/documents/{uid}")
        def delete(self, uid: str):
            """This call will delete the document for the specified uid."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class __Users(Consumer):
        """Interface to Technical Content Feedback Users resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            self._base_url = Resource._base_url
            super().__init__(base_url=self._base_url, *args, **kw)

        @returns.json
        @http_get("technical-content-feedback/users")
        def list(self, product_group_uid: Query = None, email: Query = None):
            """This call will return a list of users."""
        
        @returns.json
        @http_get("technical-content-feedback/users/{uid}")
        def get(self, uid: str):
            """This call will return an user for the specified uid."""
        
        @returns.json
        @json
        @post("technical-content-feedback/users")
        def insert(self, user: Body):
            """This call will create an  user with the specified parameters."""
        
        @json
        @patch("technical-content-feedback/users/{uid}")
        def update(self, uid: str, user: Body):
            """This call will update the user with the specified parameters."""
        
        @delete("technical-content-feedback/users/{uid}")
        def delete(self, uid: str):
            """This call will delete the user for the specified uid."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class __Assignments(Consumer):
        """Interface to Technical Content Feedback Assignments resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            self._base_url = Resource._base_url
            super().__init__(base_url=self._base_url, *args, **kw)

        @returns.json
        @http_get("technical-content-feedback/assignments")
        def list(self, product_group_uid: Query = None):
            """This call will return a list of assignments."""
        
        @returns.json
        @http_get("technical-content-feedback/assignments/{uid}")
        def get(self, uid: str):
            """This call will return an assignment for the specified uid."""

        @returns.json
        @http_get("technical-content-feedback/assignments-matrix")
        def matrix(self, product_group_uid: Query = None):
            """This call will return a matrix of assignments."""
        
        @returns.json
        @json
        @post("technical-content-feedback/assignments")
        def insert(self, assignment: Body):
            """This call will create an assignment with the specified parameters."""
        
        @json
        @patch("technical-content-feedback/assignments/{uid}")
        def update(self, uid: str, assignment: Body):
            """This call will update the assignment with the specified parameters."""
        
        @delete("technical-content-feedback/assignments/{uid}")
        def delete(self, uid: str):
            """This call will delete the assignment for the specified uid."""