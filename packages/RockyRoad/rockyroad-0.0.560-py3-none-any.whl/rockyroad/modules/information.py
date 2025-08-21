from .module_imports import key
from uplink.retry.when import status_5xx
from uplink import (
    Consumer,
    get as http_get,
    returns,
    headers,
    retry,
)

import uplink
from uplink.retry.backoff import fixed


@headers({"Ocp-Apim-Subscription-Key": key})
@retry(max_attempts=20, when=status_5xx())
class Information(Consumer):
    """Inteface to Information resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    def sites(self):
        return self.__Sites(self)

    def brands(self):
        return self.__Brands(self)

    def securityGroups(self):
        return self.__Security_Groups(self)

    def securityRoles(self):
        return self.__Security_Roles(self)

    def securityProductLines(self):
        return self.__Security_Product_Lines(self)

    def securityAreas(self):
        return self.__Security_Areas(self)

    def securityProductLineKeys(self):
        return self.__Security_Product_Line_Keys(self)

    def securityAreaKeys(self):
        return self.__Security_Area_Keys(self)

    def securityAuthMapping(self):
        return self.__Security_Auth_Mapping(self)

    def securityCompanyDesignations(self):
        return self.__Company_Designations(self)

    def portalUrls(self):
        return self.__Portal_Urls(self)

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class __Sites(Consumer):
        """Interface to Sites resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @http_get("information/sites")
        def list(
            self,
        ):
            """This call will return a list of sites."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class __Brands(Consumer):
        """Interface to Brands resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @http_get("information/brands")
        def list(
            self,
        ):
            """This call will return a list of brands."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class __Security_Groups(Consumer):
        """Interface to Security Groups resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @http_get("information/security-groups")
        def list(
            self,
        ):
            """This call will return a list of security groups."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class __Security_Roles(Consumer):
        """Interface to Security Roles resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @http_get("information/security-roles")
        def list(
            self,
        ):
            """This call will return a list of security roles."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class __Security_Product_Lines(Consumer):
        """Interface to Security Product Lines resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @http_get("information/security-product-lines")
        def list(
            self,
        ):
            """This call will return a list of security product lines."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class __Security_Areas(Consumer):
        """Interface to Security Areas resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @http_get("information/security-areas")
        def list(
            self,
        ):
            """This call will return a list of security areas."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class __Security_Product_Line_Keys(Consumer):
        """Interface to Security Product Lines resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @http_get("information/security-product-line-keys")
        def list(
            self,
        ):
            """This call will return a list of security product line keys."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class __Security_Area_Keys(Consumer):
        """Interface to Security Areas resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @http_get("information/security-area-keys")
        def list(
            self,
        ):
            """This call will return a list of security area keys."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class __Security_Auth_Mapping(Consumer):
        """Interface to Security Auth Mapping resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @http_get("information/security-auth-mapping")
        def list(
            self,
        ):
            """This call will return a mapping of security authorization keys and product lines."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class __Company_Designations(Consumer):
        """Interface to Security Company Designations resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @http_get("information/security-company-designations")
        def list(
            self,
        ):
            """This call will return a mapping of company designations."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class __Portal_Urls(Consumer):
        """Interface to Portal URLs resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @http_get("information/portal-urls")
        def list(
            self,
        ):
            """This call will return a mapping of portal URLs."""
