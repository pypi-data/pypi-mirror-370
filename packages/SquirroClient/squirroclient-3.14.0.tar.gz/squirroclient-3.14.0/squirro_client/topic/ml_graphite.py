import logging
from typing import Any, Callable

log = logging.getLogger(__name__)


class MLGraphiteMixin:
    """
    Mixin for interacting with Graphite resources.
    """

    topic_api_url: str
    tenant: str
    _perform_request: Callable[..., Any]
    _process_response: Callable

    def get_graphite_instances(self, project_id):
        """List configured Graphite instances."""
        url = f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/graphite/instances"
        headers = {"Content-Type": "application/json"}
        res = self._perform_request("get", url, headers=headers)
        return self._process_response(res)

    def get_graphite_projects(self, project_id, instance_id):
        """Get projects from Graphite."""
        url = f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/graphite/instances/{instance_id}/graphite-projects"
        headers = {"Content-Type": "application/json"}
        res = self._perform_request("get", url, headers=headers)
        return self._process_response(res)

    def get_all_graphite_projects(self, project_id):
        """Get projects from all Graphite integrations."""
        url = f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/graphite/graphite-projects"
        headers = {"Content-Type": "application/json"}
        res = self._perform_request("get", url, headers=headers)
        return self._process_response(res)

    def get_graphite_schemes(self, project_id, instance_id, graphite_project_id):
        """Get schemes from a Graphite project."""
        url = f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/graphite/instances/{instance_id}/graphite-projects/{graphite_project_id}/schemes"
        headers = {"Content-Type": "application/json"}
        res = self._perform_request("get", url, headers=headers)
        return self._process_response(res)

    def get_graphite_concepts(
        self, project_id, instance_id, graphite_project_id, scheme_id
    ):
        """Get concepts from a Graphite scheme."""
        url = f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/graphite/instances/{instance_id}/graphite-projects/{graphite_project_id}/schemes/{scheme_id}/concepts"
        headers = {"Content-Type": "application/json"}
        res = self._perform_request("get", url, headers=headers)
        return self._process_response(res)
