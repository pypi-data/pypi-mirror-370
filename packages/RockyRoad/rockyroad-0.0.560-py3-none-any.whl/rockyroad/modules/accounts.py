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
class Accounts(Consumer):
    """Inteface to accounts resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    def dealers(self):
        return self.__Dealers(self)

    def customers(self):
        return self.__Customers(self)

    def contacts(self):
        return self.__Contacts(self)

    @returns.json
    @http_get("accounts")
    def list(
        self,
        account: Query = None,
        account_uid: Query = None,
        dealer_code: Query = None,
    ):
        """This call will return detailed account information for account specified or all accounts if none is specified."""

    @delete("accounts/{uid}")
    def delete(self, uid: str):
        """This call will delete the account for the specified brand and alert request id."""

    @returns.json
    @json
    @post("accounts")
    def insert(self, new_account: Body):
        """This call will create an account with the specified parameters."""

    @json
    @patch("accounts/{uid}")
    def update(self, uid: str, account: Body):
        """This call will update an account with the specified parameters."""

    @returns.json
    @json
    @post("accounts/assign-dealer")
    def assign_dealer(
        self,
        customer_account: Query,
        dealer_account: Query,
        is_default_dealer: Query = None,
        dealer_internal_account: Query = None,
    ):
        """This call will assign the dealer for the customer with the specified parameters."""

    @returns.json
    @json
    @post("accounts/unassign-dealer")
    def unassign_dealer(
        self, customer_account: Query, dealer_account: Query
    ):
        """This call will unassign the dealer for the customer."""

    @returns.json
    @json
    @post("accounts/set-is-dealer")
    def set_is_dealer(self, account: Query, is_dealer: Query):
        """This call will set the account as a dealer account."""

    @returns.json
    @json
    @post("accounts/set-default-dealer")
    def set_default_dealer(
        self, customer_account: Query, dealer_account: Query
    ):
        """This call will set the account as a dealer account."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class __Contacts(Consumer):
        """Inteface to account contacts resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            self._base_url = Resource._base_url
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @http_get("accounts/contacts")
        def list(
            self,
            account: Query = None,
            account_uid: Query = None,
            account_contact_uid: Query = None,
            include_dealer_contacts: Query = False,
        ):
            """This call will return detailed contact information for the account specified."""

        @returns.json
        @delete("accounts/contacts")
        def delete(self, account_contact_uid: Query = None):
            """This call will delete the specified account contact."""

        @returns.json
        @json
        @post("accounts/contacts")
        def insert(self, new_account_contact: Body):
            """This call will create an account contact with the specified parameters."""

        @returns.json
        @json
        @patch("accounts/contacts")
        def update(self, account_contact: Body):
            """This call will update an account contact with the specified parameters."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class __Customers(Consumer):
        """Inteface to customers resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            self._base_url = Resource._base_url
            super().__init__(base_url=Resource._base_url, *args, **kw)

        def dealer_provided_information(self):
            return self.__DealerProvidedInformation(self)

        @returns.json
        @http_get("accounts/customers")
        def list(
            self,
            dealer_account: Query = None,
            account_association_uid: Query = None,
            dealer_uid: Query = None,
            dealer_branch_uid: Query = None,
        ):
            """This call will return detailed customer information for all accounts or for the dealer or account association specified."""

        @headers({"Ocp-Apim-Subscription-Key": key})
        @retry(max_attempts=20, when=status_5xx())
        class __DealerProvidedInformation(Consumer):
            """Inteface to dealer-provided information resource for the RockyRoad API."""

            def __init__(self, Resource, *args, **kw):
                super().__init__(base_url=Resource._base_url, *args, **kw)

            @returns.json
            @http_get("accounts/customers/dealer-provided-information")
            def list(
                self,
                dealer_account: Query = None,
                dealer_account_uid: Query = None,
                customer_account: Query = None,
                customer_account_uid: Query = None,
            ):
                """This call will return dealer-provided information for the account specified."""

            @returns.json
            @json
            @patch("accounts/customers/dealer-provided-information")
            def update(self, dealer_provided_information: Body):
                """This call will update dealer-provided information with the specified parameters."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class __Dealers(Consumer):
        """Inteface to dealers resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @http_get("accounts/dealers")
        def list(self, customer_account: Query = None):
            """This call will return detailed alert request information for the creator's email specified or all alert requests if no email is specified."""
