from ..util import _dumps


class TasksMixin:
    def get_tasks(self):
        """Return a list of all scheduled tasks for the current user."""
        # Build URL
        url = f"{self.topic_api_url}/v0/{self.tenant}/tasks"
        res = self._perform_request("get", url)
        return self._process_response(res)

    def get_task(self, task_id):
        """Return details for a scheduled task.

        :param task_id: Task identifier.
        """
        # Build URL
        url = f"{self.topic_api_url}/v0/{self.tenant}/tasks/{task_id}"
        res = self._perform_request("get", url)
        return self._process_response(res)

    def create_task(self, **params):
        """Create a scheduled task. All parameters are passed on as attributes
        to create.
        """
        # Build URL
        url = f"{self.topic_api_url}/v0/{self.tenant}/tasks"
        res = self._perform_request(
            "post",
            url,
            data=_dumps(params),
            headers={"Content-Type": "application/json"},
        )
        return self._process_response(res, [201])

    def update_task(self, task_id, **params):
        """Update a scheduled task. All parameters are passed on as attributes
        to update.

        :param task_id: Task identifier.
        """
        # Build URL
        url = f"{self.topic_api_url}/v0/{self.tenant}/tasks/{task_id}"
        res = self._perform_request(
            "put",
            url,
            data=_dumps(params),
            headers={"Content-Type": "application/json"},
        )
        return self._process_response(res)

    def delete_task(self, task_id):
        """Delete a scheduled task.

        :param task_id: Task identifier.
        """
        # Build URL
        url = f"{self.topic_api_url}/v0/{self.tenant}/tasks/{task_id}"
        res = self._perform_request("delete", url)
        self._process_response(res, [204])
