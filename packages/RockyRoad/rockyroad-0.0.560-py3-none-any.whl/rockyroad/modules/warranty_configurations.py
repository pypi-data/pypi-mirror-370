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
class _Warranty_Configurations(Consumer):
    """Inteface to warranty configurations resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    @returns.json
    @http_get("warranties/configurations/roles")
    def get_roles_configuration(
        self,
    ):
        """This call will return configuration information for warranty roles."""

    @returns.json
    @http_get("warranties/configurations/claim-process-states")
    def get_claim_process_states(
        self,
    ):
        """This call will return configuration information for claim process states."""

    @returns.json
    @http_get("warranties/configurations/claim-settings")
    def get_claim_settings(
        self,
    ):
        """This call will return configuration information for claim settings."""

    @returns.json
    @http_get("warranties/configurations/claim-process-transitions")
    def get_claim_process_transitions(
        self,
        state: Query = None,
        roles: Query = None,
        claim_level: Query = None,
        is_hub_claim: Query = None,
    ):
        """This call will return configuration information for claim process transitions."""

    @returns.json
    @http_get("warranties/configurations/warranty-role-tests")
    def get_warranty_role_tests(
        self,
        hub_claim_option: Query = None,
        included_states: Query = None,
        included_claim_levels: Query = None,
        included_test_users: Query = None,
        excluded_states: Query = None,
        excluded_claim_levels: Query = None,
        excluded_test_users: Query = None,
    ):
        """This call will return configuration information for warranty role tests."""

    @returns.json
    @http_get("warranties/configurations/warranty-test-users")
    def get_warranty_test_users(
        self,
    ):
        """This call will return configuration information for warranty test users."""

    @returns.json
    @http_get("warranties/configurations/warranty-test-fixtures")
    def get_warranty_test_fixtures(
        self,
    ):
        """This call will return configuration information for warranty test fixtures."""

    @returns.json
    @http_get("warranties/configurations/warranty-role-based-access-tests")
    def get_warranty_role_based_access_tests(self):
        """This call will return configuration information for warranty role based access tests."""

    @returns.json
    @http_get("warranties/configurations/warranty-test-scenarios")
    def get_warranty_test_scenarios(self):
        """This call will return configuration information for warranty wcr test scenarios."""

    @returns.json
    @http_get("warranties/configurations/warranty-test-rigor-scenarios")
    def get_warranty_test_rigor_scenarios(self):
        """This call will return configuration information for warranty wcr test scenarios."""

    @returns.json
    @http_get("warranties/configurations/warranty-test-scenario-matrix")
    def get_warranty_test_scenario_matrix(
        self,
        hub_claim_option: Query = None,
        included_states: Query = None,
        included_claim_levels: Query = None,
        included_test_users: Query = None,
        excluded_states: Query = None,
        excluded_claim_levels: Query = None,
        excluded_test_users: Query = None,
    ):
        """This call will return configuration information for warranty role test scenario matrix."""
