from .module_imports import key
from uplink.retry.when import status_5xx
from uplink import (
    Consumer,
    get as http_get,
    returns,
    headers,
    retry,
    json,
    patch,
    post,
    delete,
    Body,
)


@headers({"Ocp-Apim-Subscription-Key": key})
@retry(max_attempts=20, when=status_5xx())
class Users(Consumer):
    """Inteface to users resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    def settings(self):
        return self.__Settings(self)

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class __Settings(Consumer):
        """Interface to user settings resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            self._base_url = Resource._base_url
            super().__init__(base_url=self._base_url, *args, **kw)

        @returns.json
        @http_get("users/settings")
        def list(
            self,
            ):
            """This call will return user settings."""

        @returns.json
        @http_get("users/{user_uid}/settings")
        def get(
            self,
            user_uid: str,
            ):
            """This call will return user settings for the specified user uid."""

        @json
        @patch("users/{user_uid}/settings")
        def update(self, user_uid: str, settings: Body):
            """This call will update user settings for the specified user uid."""
        
        @json
        @post("users/{user_uid}/settings")
        def insert(self, user_uid: str, settings: Body):
            """This call will insert user settings for the specified user uid."""
        
        @delete("users/{user_uid}/settings")
        def delete(self, user_uid: str):
            """This call will delete user settings for the specified user uid."""

