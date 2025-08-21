import logging

log = logging.getLogger(__name__)


class ExecutionError(Exception):
    """Error in executing a machine learning job"""

    pass


class MLSentenceSplitterMixin:
    #
    #  ML Sentence Splitter
    #
    def get_sentence_splitters(self, project_id):
        """Return all available Sentence Splitter.

        :param project_id: Id of the Squirro project.
        """
        url = f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/ml_sentence_splitter"

        headers = {"Content-Type": "application/json"}
        res = self._perform_request("get", url, headers=headers)
        return self._process_response(res)
