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
class Template_Parent(Consumer):
    """Inteface to Template_Parent resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    def template_child(self):
        return self.Template_Child(self)

    @returns.json
    @http_get("template/path")
    def list(self, param: Query = None):
        """This call will return list of Template_Parent_Objects."""

    @returns.json
    @http_get("template/path/{uid}")
    def get(self, uid: str):
        """This call will get the Template_Parent_Object for the specified uid."""

    @delete("template/path/{uid}")
    def delete(self, uid: str):
        """This call will delete the Template_Parent_Object for the specified uid."""

    @returns.json
    @json
    @post("template/path")
    def insert(self, template_parent_object: Body):
        """This call will create the Template_Parent_Object with the specified parameters."""

    @json
    @patch("template/path/{uid}")
    def update(self, uid: str, template_parent_object: Body):
        """This call will update the Template_Parent_Object with the specified parameters."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    @retry(max_attempts=20, when=status_5xx())
    class Template_Child(Consumer):
        """Inteface to Template_Child resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            self._base_url = Resource._base_url
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @http_get("template/path/child")
        def list(
            self,
            param: Query = None,
        ):
            """This call will return list of Template_Childs."""

        @returns.json
        @http_get("template/path/child/{uid}")
        def get(self, uid: str):
            """This call will return list of Template_Childs."""

        @delete("template/path/child/{uid}")
        def delete(self, uid: str):
            """This call will the Template_Child."""

        @returns.json
        @json
        @post("template/path/{template_uid}/child")
        def insert(self, template_uid: str, template_child_object: Body):
            """This call will create the Template_Child."""

        @json
        @patch("template/path/child/{uid}")
        def update(self, uid: str, template_child_object: Body):
            """This call will update the Template_Child."""
