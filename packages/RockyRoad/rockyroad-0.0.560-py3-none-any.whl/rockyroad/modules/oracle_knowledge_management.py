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
class _Oracle_Knowledge_Management(Consumer):
    """Inteface to Oracle knowledge management resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    @returns.json
    @http_get("oracle/content/articles")
    def list_articles(
        self,
        limit: Query = None
    ):
        """This call will return the Oracle knowledge base article for the specified answer id."""

    @returns.json
    @http_get("oracle/content/articles/{answer_id}")
    def get_article(
        self,
        answer_id: str
    ):
        """This call will return the Oracle knowledge base article for the specified answer id."""

    @returns.json
    @http_get("oracle/search/question/")
    def get_search_results(
        self,
        question: Query,
        facet: Query = None,
        include_multi_facets: Query = None,
    ):
        """This call will return search results from Oracle knowledge management"""

    @returns.json
    @http_get("oracle/content/categories")
    def list_oracle_categories(
        self,
        limit: Query = None
    ):
        """This call will return categories from Oracle knowledge management"""

    @returns.json
    @http_get("oracle/facet-mappings")
    def get_facet_mappings(
        self,
    ):
        """This call will return categories from Oracle knowledge management"""
