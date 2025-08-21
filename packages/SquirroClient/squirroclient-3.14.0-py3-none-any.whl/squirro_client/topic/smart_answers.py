import logging

from ..util import _dumps

log = logging.getLogger(__name__)


class SmartAnswersMixin:
    def get_similar_searches(
        self, project_id: str, query: str, options: dict = None
    ) -> dict:
        """Find similar searches in popular queries given the input query

        :param project_id: Id of the Squirro project.
        :param query: The query that is used to find similar searches.
        :param options: An optional dictionary to override default options
        """
        url = (
            f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}"
            "/smart_answers/similar_searches"
        )
        headers = {"Content-Type": "application/json"}
        params = {"query": query, "options": _dumps(options)}
        res = self._perform_request("get", url, headers=headers, params=params)
        return self._process_response(res)["result"]
