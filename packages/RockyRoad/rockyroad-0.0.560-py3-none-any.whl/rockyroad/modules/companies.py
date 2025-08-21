from .module_imports import get_key
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

USE_SERVICES_API = True
key = get_key(use_services_api=USE_SERVICES_API)

@headers({"Ocp-Apim-Subscription-Key": key})
@retry(max_attempts=20, when=status_5xx())
class Companies(Consumer):
    """Inteface to Companies resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        self._services_base_url = Resource._services_base_url
        base_url = Resource._services_base_url if USE_SERVICES_API else Resource._base_url
        super().__init__(base_url=base_url, *args, **kw)

    def branches(self):
        return self.__Branches(self)

    def subscribers(self):
        return self.__Subscribers(self)

    def dealers(self):
        return self.__Dealers(self)

    def customers(self):
        return self.__Customers(self)

    def contacts(self):
        return self.__Contacts(self)

    def aliases(self):
        return self.__Aliases(self)

    @returns.json
    @http_get("companies")
    def list(
        self,
        company_name: Query = None,
        company_account: Query = None,
        company_account_uid: Query = None,
        is_dealer: Query = None,
        email_domain: Query = None,
        has_company_designation: Query = None,
        company_designation: Query = None,
        exact_match: Query = None,
        fuzzy_match: Query = None,
        fuzzy_match_limit: Query = None,
        fuzzy_scorer: Query = None,
    ):
        """This call will return detailed information for all companies or for those for the specified criteria."""

    @returns.json
    @http_get("companies/v2")
    def list_v2(
        self,
        company_name: Query = None,
        company_account: Query = None,
        company_account_uid: Query = None,
        is_dealer: Query = None,
        email_domain: Query = None,
        has_company_designation: Query = None,
        company_designation: Query = None,
        exact_match: Query = None,
        fuzzy_match: Query = None,
        fuzzy_match_limit: Query = None,
        fuzzy_scorer: Query = None,
    ):
        """This call will return basic name information for all companies or for those for the specified criteria."""

    @returns.json
    @http_get("companies/active-dealers")
    def list_active_dealers(
        self,
        company_designation: Query = None,
        in_active_dealer_listing: Query = None,
        limit: Query = None,
    ):
        """This call will return the active dealer list."""

    
    @json
    @patch("companies/active-dealers")
    def update_active_dealer(self, active_dealer: Body):
        """This call will update the active dealer listing."""

    @returns.json
    @json
    @post("companies")
    def insert(self, company: Body):
        """This call will create a company with the specified parameters."""

    @json
    @patch("companies/{uid}/merge")
    def merge(self, uid: str, body: Body):
        """This call will merge the companies listed in the body into the company with the specified uid."""

    @returns.json
    @http_get("companies/{uid}")
    def get(
        self,
        uid: str,
    ):
        """This call will return detailed information for the specified company."""

    @delete("companies/{uid}")
    def delete(self, uid: str):
        """This call will delete the company for the specified uid."""

    @json
    @patch("companies/{uid}")
    def update(self, uid: str, company: Body):
        """This call will update the company with the specified parameters."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class __Subscribers(Consumer):
        """Inteface to company Subscribers resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            base_url = Resource._services_base_url if USE_SERVICES_API else Resource._base_url
            super().__init__(base_url=base_url, *args, **kw)

        @returns.json
        @http_get("companies/{company_uid}/subscribed-users")
        def list(
            self,
            company_uid: str,
        ):
            """This call will return detailed information for all company subscribers or for those for the specified criteria."""

        @returns.json
        @http_get("companies/{company_uid}/subscribed-users/{user_uid}")
        def get(self, company_uid: str, user_uid: str):
            """This call will return detailed information for a single subscriber."""

        @delete("companies/{company_uid}/subscribed-users/{user_uid}")
        def delete(
            self,
            company_uid: str,
            user_uid: str,
        ):
            """This call will delete the company subscriber for the specified uid."""

        @post("companies/{company_uid}/subscribed-users/{user_uid}")
        def insert(self, company_uid: str, user_uid: str):
            """This call will create a company subscriber with the specified parameters."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class __Dealers(Consumer):
        """Inteface to company dealers resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            base_url = Resource._services_base_url if USE_SERVICES_API else Resource._base_url
            super().__init__(base_url=base_url, *args, **kw)

        @returns.json
        @http_get("companies/{company_uid}/dealers")
        def list(
            self,
            company_uid: str,
        ):
            """This call will return detailed information for all dealers supporting the customer company uid."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class __Customers(Consumer):
        """Inteface to company customers resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            base_url = Resource._services_base_url if USE_SERVICES_API else Resource._base_url
            super().__init__(base_url=base_url, *args, **kw)

        @returns.json
        @http_get("companies/{company_uid}/customers")
        def list(
            self,
            company_uid: str,
        ):
            """This call will return detailed information for all company subscribers or for those for the specified criteria."""

        @returns.json
        @json
        @post("companies/{company_uid}/customers/{customer_uid}")
        def insert(
            self, company_uid: str, customer_uid: str, dealer_information: Body = None
        ):
            """This call will assign company to dealer."""

        @delete("companies/{company_uid}/customers/{customer_uid}")
        def delete(
            self,
            company_uid: str,
            customer_uid: str,
        ):
            """This call will unassign company from dealer."""

        @json
        @patch("companies/{company_uid}/customers/{customer_uid}")
        def update(self, company_uid: str, customer_uid: str, dealer_information: Body):
            """This call will update the dealer information."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class __Contacts(Consumer):
        """Inteface to company contacts resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            base_url = Resource._services_base_url if USE_SERVICES_API else Resource._base_url
            super().__init__(base_url=base_url, *args, **kw)

        @returns.json
        @http_get("companies/{company_uid}/customers/{customer_uid}/contacts")
        def list(self, company_uid: str, customer_uid: str):
            """This call will return list of company contacts."""

        @returns.json
        @json
        @post("companies/{company_uid}/customers/{customer_uid}/contacts")
        def insert(
            self, company_uid: str, customer_uid: str, contact_information: Body
        ):
            """This call will add new company contact."""

        @delete("companies/contacts/{uid}")
        def delete(
            self,
            uid: str,
        ):
            """This call will delete the company contact."""

        @patch("companies/contacts/{uid}")
        def get(self, uid: str, contact_information: Body):
            """This call will update the contact information."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class __Branches(Consumer):
        """Inteface to company Branches resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            base_url = Resource._services_base_url if USE_SERVICES_API else Resource._base_url
            super().__init__(base_url=base_url, *args, **kw)

        def subscribers(self):
            return self.__Subscribers(self)

        @returns.json
        @http_get("companies/{company_uid}/branches")
        def list_for(
            self,
            company_uid: str,
            has_warranty_rates: Query = None,
            in_active_dealer_listing: Query = None,
            is_inventory_reporting_branch: Query = None,
        ):
            """This call will return detailed branch information for the specified company."""

        @returns.json
        @json
        @post("companies/{company_uid}/branches")
        def insert(self, company_uid: str, branch: Body):
            """This call will create a company branch  with the specified parameters."""

        @returns.json
        @http_get("branches")
        def list(
            self,
            include_machines: Query = None,
            has_warranty_rates: Query = None,
            in_active_dealer_listing: Query = None,
            is_inventory_reporting_branch: Query = None,
        ):
            """This call will return detailed information for all branches."""

        @returns.json
        @http_get("branches/{uid}")
        def get(self, uid: str):
            """This call will return detailed branch information for the specified uid."""

        @delete("branches/{uid}")
        def delete(self, uid: str):
            """This call will delete the company branch for the specified uid."""

        @json
        @patch("branches/{uid}")
        def update(self, uid: str, branch: Body):
            """This call will update the company branch  with the specified parameters."""

        @headers({"Ocp-Apim-Subscription-Key": key})
        @retry(max_attempts=20, when=status_5xx())
        class __Subscribers(Consumer):
            """Inteface to company Branch Subscribers resource for the RockyRoad API."""

            def __init__(self, Resource, *args, **kw):
                base_url = Resource._services_base_url if USE_SERVICES_API else Resource._base_url
                super().__init__(base_url=base_url, *args, **kw)

            @returns.json
            @http_get("branches/{branch_uid}/subscribed-users")
            def list(self, branch_uid: str):
                """This call will return detailed information for company branch subscribers."""

            @delete("branches/{branch_uid}/subscribed-users/{user_uid}")
            def delete(self, branch_uid: str, user_uid: str):
                """This call will delete the company branch subscriber for the specified uid."""

            @post("branches/{branch_uid}/subscribed-users/{user_uid}")
            def insert(self, branch_uid: str, user_uid: str):
                """This call will create a company branch subscriber."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class __Aliases(Consumer):
        """Inteface to company aliases resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            base_url = Resource._services_base_url if USE_SERVICES_API else Resource._base_url
            super().__init__(base_url=base_url, *args, **kw)

        @returns.json
        @http_get("companies/aliases")
        def list(
            self,
            alias: Query = None,
            exact_match: Query = None
        ):
            """This call will return detailed information for all aliases."""

        @returns.json
        @http_get("companies/{company_uid}/aliases")
        def list_for(
            self,
            company_uid: str,
        ):
            """This call will return aliases for the specified company."""

        @returns.json
        @json
        @post("companies/{company_uid}/aliases")
        def insert(self, company_uid: str, alias: Body):
            """This call will create an alias for the specified company."""

        @delete("companies/aliases/{uid}")
        def delete(self, uid: str):
            """This call will delete the alias for the specified uid."""

        @json
        @patch("companies/aliases/{uid}")
        def update(self, uid: str, alias: Body):
            """This call will update the alias with the specified parameters."""
