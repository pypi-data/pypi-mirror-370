from typing import Any, Callable


class GenAIApiMixin:
    _genai_api_url: str
    _perform_request: Callable[..., Any]
    _process_response: Callable

    @property
    def genai_api_url(self):
        if not self._genai_api_url:
            raise ValueError(
                "`genai_api_url` is not set. Please initialize the SquirroClient with a valid `genai_api_url` to interact with the GenAI API."
            )
        return self._genai_api_url

    @genai_api_url.setter
    def genai_api_url(self, value):
        self._genai_api_url = value

    def genai_request(self, method, route, **kwargs):
        """
        Perform a generic request to the GenAI API.

        Example:

        ```python
        client.genai_request(
            "post",
            "/v0/arbitrary_prompt",
            json={
                "question_prompt": "What is the capital of France?",
                "runtime_config": {"llm_api_key": "<API_KEY>"},
            },
        )
        ```
        """
        return self._perform_request(method, self.genai_api_url + route, **kwargs)

    # TODO: Add method for streaming chat endpoint and then refactor Studio Plugin to use this client for the streaming chat invocation (need to deal with streaming).

    def genai_post_arbitrary_prompt(self, data):
        """Post an arbitrary prompt to the GenAI API."""
        url = self.genai_api_url + "/v0/arbitrary_prompt"
        res = self._perform_request("post", url, json=data)

        return self._process_response(res)

    def get_agents(self, project_id: str):
        """Get all Squirro Chat Agents for a given project."""
        url = self.genai_api_url + f"/v0/projects/{project_id}/agents/"
        res = self._perform_request("get", url)
        return self._process_response(res)

    def get_agent(self, project_id: str, agent_id: str):
        """Get a specific Squirro Chat Agent."""
        url = self.genai_api_url + f"/v0/projects/{project_id}/agents/{agent_id}"
        res = self._perform_request("get", url)

        return self._process_response(res)

    def create_agent(self, project_id: str, data):
        """Create a new Squirro Chat Agent."""
        url = self.genai_api_url + f"/v0/projects/{project_id}/agents/"
        res = self._perform_request("post", url, json=data)

        return self._process_response(res, [200])  # we might need to adjust to [201]

    def delete_agent(self, project_id: str, agent_id: str):
        """Delete a specific Squirro Chat Agent."""
        url = self.genai_api_url + f"/v0/projects/{project_id}/agents/{agent_id}"
        res = self._perform_request("delete", url)

        return self._process_response(res, [200])  # we might need to adjust to [204]

    def update_agent(self, project_id: str, agent_id: str, data):
        """Update a specific Squirro Chat Agent."""
        url = self.genai_api_url + f"/v0/projects/{project_id}/agents/{agent_id}"
        res = self._perform_request("patch", url, json=data)

        return self._process_response(res)

    def move_agent(self, project_id: str, agent_id: str, data):
        """Change the presentation order of a specific Squirro Chat Agent."""
        url = self.genai_api_url + f"/v0/projects/{project_id}/agents/{agent_id}/move"
        res = self._perform_request("post", url, json=data)

        return self._process_response(res, [200])  # we might need to adjust to [204]

    def import_agents(self, project_id: str, data):
        """Import Squirro Chat Agents."""
        url = self.genai_api_url + f"/v0/projects/{project_id}/agents/import"
        res = self._perform_request("post", url, json=data)

        return self._process_response(res)

    def delete_all_agents(self, project_id: str):
        """Delete all Squirro Chat Agents for a given project."""
        url = self.genai_api_url + f"/v0/projects/{project_id}/agents/delete_all_agents"
        res = self._perform_request("post", url)

        return self._process_response(res, [200])  # we might need to adjust to [204]
