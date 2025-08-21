from typing import Any, Callable


class SearchApiMixin:
    _search_api_url: str = None
    _perform_request: Callable[..., Any]
    _process_response: Callable

    @property
    def search_api_url(self):
        if not self._search_api_url:
            raise ValueError(
                "`search_api_url` is not set. Please initialize the SquirroClient with a valid `search_api_url` to interact with the Search API."
            )
        return self._search_api_url

    @search_api_url.setter
    def search_api_url(self, value):
        self._search_api_url = value

    def tokenize_query(self, query: str, timing: bool = False) -> dict:
        """
        Endpoint to tokenize query.

        It receives as input a query, and returns the tokenized query.

        Args:
            query: The query to tokenize
            timing: Whether to include timing information in the response

        Returns:
            QueryLexerResponse: Contains the tokenized query
        """
        url = self.search_api_url + "/v0/query/lexer"
        params = {"query": query, "timing": timing}
        res = self._perform_request("get", url, params=params)

        return self._process_response(res)

    def parse_query(self, query: str, timing: bool = False) -> dict:
        """
        Endpoint to parse query.

        It receives as input a query, and returns the parsed query.

        Args:
            query: The query to parse
            timing: Whether to include timing information in the response

        Returns:
            QueryParserResponse: Contains the parsed query
        """
        url = self.search_api_url + "/v0/query/parser"
        params = {"query": query, "timing": timing}
        res = self._perform_request("get", url, params=params)

        return self._process_response(res)

    def generate_search_query(self, query: str, timing: bool = False) -> dict:
        """
        Endpoint to generate search query.

        It receives as input a query, and returns the generated search query.

        Args:
            query: The query to generate a search query for
            timing: Whether to include timing information in the response

        Returns:
            QueryGeneratorResponse: Contains the generated search query
        """
        url = self.search_api_url + "/v0/query/generator"
        params = {"query": query, "timing": timing}
        res = self._perform_request("get", url, params=params)

        return self._process_response(res)

    def get_service_status(self) -> dict:
        """
        Get Service Status.

        Will return `OK` if everything is fine and a list of dead
        thread/sub-processes from the watchdog if something is amiss.

        Returns:
            ServiceStatus: Contains the status of the service
        """
        url = self.search_api_url + "/_internal/status"
        res = self._perform_request("get", url)

        return self._process_response(res)
