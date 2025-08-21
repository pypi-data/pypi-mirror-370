import logging
from typing import Optional

from ..util import _dumps

log = logging.getLogger(__name__)


class MLNerMixin:
    """
    Mixin for interacting with NER groundtruths, categories, labels, and models.
    """

    #
    # Ground Truths
    #

    def get_ner_groundtruths(self, project_id):
        """List all groundtruths for a project."""
        url = f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/ner/groundtruths"
        headers = {"Content-Type": "application/json"}
        res = self._perform_request("get", url, headers=headers)
        return self._process_response(res)

    def get_groundtruths_ner(self, project_id):
        """Return all ground truth for a project in a list.

        :param project_id: Id of the Squirro project.
        """

        base_url = "{}/v0/{}/projects/{}/groundtruths"
        url = base_url.format(self.topic_api_url, self.tenant, project_id)

        headers = {"Content-Type": "application/json"}
        res = self._perform_request("get", url, headers=headers)
        return self._process_response(res)

    def get_ner_groundtruth(self, project_id, groundtruth_id):
        """Retrieve a single groundtruth by ID."""
        url = (
            f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}"
            f"/ner/groundtruths/{groundtruth_id}"
        )
        headers = {"Content-Type": "application/json"}
        res = self._perform_request("get", url, headers=headers)
        return self._process_response(res)

    def create_ner_groundtruth(self, project_id, groundtruth_data):
        """Create a new groundtruth."""
        url = f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/ner/groundtruths"
        headers = {"Content-Type": "application/json"}
        res = self._perform_request(
            "post", url, data=_dumps(groundtruth_data), headers=headers
        )
        return self._process_response(res)

    def update_ner_groundtruth(self, project_id, groundtruth_id, groundtruth_data):
        """Update an existing groundtruth."""
        url = (
            f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}"
            f"/ner/groundtruths/{groundtruth_id}"
        )
        headers = {"Content-Type": "application/json"}
        res = self._perform_request(
            "put", url, data=_dumps(groundtruth_data), headers=headers
        )
        return self._process_response(res)

    def delete_ner_groundtruth(self, project_id, groundtruth_id):
        """Delete a groundtruth."""
        url = (
            f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}"
            f"/ner/groundtruths/{groundtruth_id}"
        )
        headers = {"Content-Type": "application/json"}
        res = self._perform_request("delete", url, headers=headers)
        return self._process_response(res, [200, 204])

    #
    # Categories
    #

    def get_ner_categories(self, project_id, groundtruth_id):
        """List all categories under a groundtruth."""
        url = (
            f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}"
            f"/ner/groundtruths/{groundtruth_id}/categories"
        )
        headers = {"Content-Type": "application/json"}
        res = self._perform_request("get", url, headers=headers)
        return self._process_response(res)

    def get_ner_category(self, project_id, groundtruth_id, category_id):
        """Retrieve a single category."""
        url = (
            f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}"
            f"/ner/groundtruths/{groundtruth_id}/categories/{category_id}"
        )
        headers = {"Content-Type": "application/json"}
        res = self._perform_request("get", url, headers=headers)
        return self._process_response(res)

    def create_ner_category(self, project_id, groundtruth_id, category_data):
        """Create a new category."""
        url = (
            f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}"
            f"/ner/groundtruths/{groundtruth_id}/categories"
        )
        headers = {"Content-Type": "application/json"}
        res = self._perform_request(
            "post", url, data=_dumps(category_data), headers=headers
        )
        return self._process_response(res, [200])

    def update_ner_category(
        self, project_id, groundtruth_id, category_id, category_data
    ):
        """Update an existing category."""
        url = (
            f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}"
            f"/ner/groundtruths/{groundtruth_id}/categories/{category_id}"
        )
        headers = {"Content-Type": "application/json"}
        res = self._perform_request(
            "put", url, data=_dumps(category_data), headers=headers
        )
        return self._process_response(res)

    def delete_ner_category(self, project_id, groundtruth_id, category_id):
        """Delete a category."""
        url = (
            f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}"
            f"/ner/groundtruths/{groundtruth_id}/categories/{category_id}"
        )
        headers = {"Content-Type": "application/json"}
        res = self._perform_request("delete", url, headers=headers)
        return self._process_response(res, [200, 204])

    #
    # Labels
    #

    def get_ner_labels(self, project_id, groundtruth_id, category_id):
        """List all labels for a category."""
        url = (
            f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}"
            f"/ner/groundtruths/{groundtruth_id}/categories/{category_id}/labels"
        )
        headers = {"Content-Type": "application/json"}
        res = self._perform_request("get", url, headers=headers)
        return self._process_response(res)

    def get_ner_label(self, project_id, groundtruth_id, category_id, label_id):
        """Retrieve a single label."""
        url = (
            f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}"
            f"/ner/groundtruths/{groundtruth_id}/categories/{category_id}/labels/{label_id}"
        )
        headers = {"Content-Type": "application/json"}
        res = self._perform_request("get", url, headers=headers)
        return self._process_response(res)

    def create_ner_label(self, project_id, groundtruth_id, category_id, label_data):
        """Create a new label."""
        url = (
            f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}"
            f"/ner/groundtruths/{groundtruth_id}/categories/{category_id}/labels"
        )
        headers = {"Content-Type": "application/json"}
        res = self._perform_request(
            "post", url, data=_dumps(label_data), headers=headers
        )
        return self._process_response(res)

    def update_ner_label(
        self, project_id, groundtruth_id, category_id, label_id, label_data
    ):
        """Update an existing label."""
        url = (
            f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}"
            f"/ner/groundtruths/{groundtruth_id}/categories/{category_id}/labels/{label_id}"
        )
        headers = {"Content-Type": "application/json"}
        res = self._perform_request(
            "put", url, data=_dumps(label_data), headers=headers
        )
        return self._process_response(res)

    def delete_ner_label(self, project_id, groundtruth_id, category_id, label_id):
        """Delete a label."""
        url = (
            f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}"
            f"/ner/groundtruths/{groundtruth_id}/categories/{category_id}/labels/{label_id}"
        )
        headers = {"Content-Type": "application/json"}
        res = self._perform_request("delete", url, headers=headers)
        return self._process_response(res, [200, 204])

    #
    # Models
    #

    def get_ner_models(self, project_id):
        """List all available NER models."""
        url = f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/ner/models"
        headers = {"Content-Type": "application/json"}
        res = self._perform_request("get", url, headers=headers)
        return self._process_response(res)

    #
    # Ground Truth Item Labels
    #

    def get_ner_item_labels(
        self,
        project_id,
        groundtruth_id,
        user_id=None,
        labelled_filter=None,
        label_id=None,
        query=None,
        count=None,
        start=None,
    ):
        """List all item labels for a groundtruth, with optional filters."""
        url = (
            f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}"
            f"/ner/groundtruths/{groundtruth_id}/items"
        )
        headers = {"Content-Type": "application/json"}
        # Build query parameters dynamically
        params = {
            "user_id": user_id,
            "labelled_filter": labelled_filter,
            "label_id": label_id,
            "query": query,
            "count": count,
            "start": start,
        }
        # Remove None values
        filtered_params = {k: v for k, v in params.items() if v is not None}

        # Perform request with query parameters
        res = self._perform_request("get", url, headers=headers, params=filtered_params)
        return self._process_response(res)

    def get_ner_item_label(self, project_id, groundtruth_id, item_id):
        """Get all labels for a specific item."""
        url = (
            f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}"
            f"/ner/groundtruths/{groundtruth_id}/items/{item_id}"
        )
        headers = {"Content-Type": "application/json"}
        res = self._perform_request("get", url, headers=headers)
        return self._process_response(res)

    def create_ner_item_label(self, project_id, groundtruth_id, item_id, label_data):
        """Create a new label for a groundtruth item."""
        url = (
            f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}"
            f"/ner/groundtruths/{groundtruth_id}/items/{item_id}/labels"
        )
        headers = {"Content-Type": "application/json"}
        res = self._perform_request(
            "post", url, data=_dumps(label_data), headers=headers
        )
        return self._process_response(res)

    def update_ner_item_label(
        self, project_id, groundtruth_id, item_id, item_label_id, label_data
    ):
        """Update a label on a groundtruth item."""
        url = (
            f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}"
            f"/ner/groundtruths/{groundtruth_id}/items/{item_id}/labels/{item_label_id}"
        )
        headers = {"Content-Type": "application/json"}
        res = self._perform_request(
            "put", url, data=_dumps(label_data), headers=headers
        )
        return self._process_response(res)

    def delete_ner_item_label(self, project_id, groundtruth_id, item_id, item_label_id):
        """Delete a specific label from a groundtruth item."""
        url = (
            f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}"
            f"/ner/groundtruths/{groundtruth_id}/items/{item_id}/labels/{item_label_id}"
        )
        headers = {"Content-Type": "application/json"}
        res = self._perform_request("delete", url, headers=headers)
        return self._process_response(res, [200, 204])

    #
    # Ground Truth Validation Set
    #
    def get_ner_validation_set(
        self, project_id, groundtruth_id, params: Optional[dict] = None
    ):
        """
        Get the validation set for a groundtruth.

        :param project_id: ID of the Squirro project.
        :param groundtruth_id: ID of the groundtruth.
        :param params: Optional parameters to filter the validation set. These are defined in the ML API documentation.
        """
        url = (
            f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}"
            f"/ner/groundtruths/{groundtruth_id}/validation_set"
        )
        headers = {"Content-Type": "application/json"}

        if params is None:
            params = {}

        res = self._perform_request("get", url, headers=headers, params=params)
        return self._process_response(res)

    #
    # FastPass
    #

    def get_ner_fastpass(self, project_id, groundtruth_id):
        """
        Retrieve the active FastPass settings for this project/groundtruth.
        """
        url = (
            f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}"
            f"/ner/groundtruths/{groundtruth_id}/fastpass"
        )
        headers = {"Content-Type": "application/json"}
        res = self._perform_request("get", url, headers=headers)
        return self._process_response(res)

    def create_ner_fastpass(self, project_id, groundtruth_id, fastpass_data):
        """
        Create or overwrite (upsert) the FastPass settings.
        """
        url = (
            f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}"
            f"/ner/groundtruths/{groundtruth_id}/fastpass"
        )
        headers = {"Content-Type": "application/json"}
        res = self._perform_request(
            "post", url, data=_dumps(fastpass_data), headers=headers
        )
        # upsert returns 201 on success
        return self._process_response(res)

    def update_ner_fastpass(self, project_id, groundtruth_id, fastpass_update):
        """
        Toggle only the `active` flag on the FastPass.
        """
        url = (
            f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}"
            f"/ner/groundtruths/{groundtruth_id}/fastpass"
        )
        headers = {"Content-Type": "application/json"}
        res = self._perform_request(
            "put", url, data=_dumps(fastpass_update), headers=headers
        )
        return self._process_response(res)

    def delete_ner_fastpass(self, project_id, groundtruth_id):
        """
        Soft-delete the FastPass (set `active = False`).
        """
        url = (
            f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}"
            f"/ner/groundtruths/{groundtruth_id}/fastpass"
        )
        headers = {"Content-Type": "application/json"}
        res = self._perform_request("delete", url, headers=headers)
        # backend returns 200 or 204
        return self._process_response(res, expected_status=[200, 204])

    def get_ner_fastpass_models(self, project_id, groundtruth_id):
        """
        List all FastPass templates available for NER.
        """
        url = (
            f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}"
            f"/ner/groundtruths/{groundtruth_id}/fastpass/models"
        )
        headers = {"Content-Type": "application/json"}
        res = self._perform_request("get", url, headers=headers)
        return self._process_response(res)

    def get_ner_fastpass_labels(
        self,
        project_id,
        groundtruth_id,
        item_id,
        label_mapping=None,
        config_model=None,
    ):
        """
        Run FastPass inference on a single item.
        Optional query parameters (e.g. label_mapping, config_model) will be forwarded.
        """
        url = (
            f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}"
            f"/ner/groundtruths/{groundtruth_id}/fastpass/{item_id}/labels"
        )
        headers = {"Content-Type": "application/json"}

        # build query‐string params, drop None values
        params = {
            "label_mapping": label_mapping,
            "config_model": config_model,
        }
        params = {k: v for k, v in params.items() if v is not None}

        res = self._perform_request("get", url, headers=headers, params=params)
        return self._process_response(res)

    def get_ner_publishes(self, project_id, groundtruth_id):
        """List all published NER models for a groundtruth."""
        url = (
            f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}"
            f"/ner/groundtruths/{groundtruth_id}/publish"
        )
        headers = {"Content-Type": "application/json"}
        res = self._perform_request("get", url, headers=headers)
        return self._process_response(res)

    def get_all_ner_publishes(self, project_id):
        """List all published NER models for a groundtruth."""
        url = f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/ner/publish"
        headers = {"Content-Type": "application/json"}
        res = self._perform_request("get", url, headers=headers)
        return self._process_response(res)

    def create_ner_publish(self, project_id, groundtruth_id, publish_data):
        """Create and publish a new NER model."""
        url = (
            f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}"
            f"/ner/groundtruths/{groundtruth_id}/publish"
        )
        headers = {"Content-Type": "application/json"}
        res = self._perform_request(
            "post", url, data=_dumps(publish_data), headers=headers
        )
        return self._process_response(res)

    def delete_ner_publish(self, project_id, groundtruth_id, publish_id):
        """Delete a published NER model."""
        url = (
            f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}"
            f"/ner/groundtruths/{groundtruth_id}/publish/{publish_id}"
        )
        headers = {"Content-Type": "application/json"}
        res = self._perform_request("delete", url, headers=headers)
        return self._process_response(res)

    def update_ner_fastpass_suggestion(
        self,
        project_id: str,
        groundtruth_id: str,
        suggestion_id: str,
        suggestion_data: dict,
    ):
        """
        Process (update) a single FastPass suggestion by its ID.
        """
        url = (
            f"{self.topic_api_url}/v0/{self.tenant}"
            f"/projects/{project_id}/ner/groundtruths/{groundtruth_id}"
            f"/fastpass/suggestions/{suggestion_id}"
        )
        headers = {"Content-Type": "application/json"}
        res = self._perform_request(
            "put",
            url,
            data=_dumps(suggestion_data),
            headers=headers,
        )
        return self._process_response(res)

    #
    # Validations
    #
    def get_ner_validations(self, project_id, groundtruth_id):
        """List all NER validations for a groundtruth."""
        url = (
            f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}"
            f"/ner/groundtruths/{groundtruth_id}/validations"
        )
        headers = {"Content-Type": "application/json"}
        res = self._perform_request("get", url, headers=headers)
        return self._process_response(res)

    def create_ner_validation(self, project_id, groundtruth_id, validation_data):
        """Create a new NER validation."""
        url = (
            f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}"
            f"/ner/groundtruths/{groundtruth_id}/validations"
        )
        headers = {"Content-Type": "application/json"}
        res = self._perform_request(
            "post", url, data=_dumps(validation_data), headers=headers
        )
        return self._process_response(res)

    def get_ner_validation(self, project_id, groundtruth_id, validation_id):
        """Retrieve a specific NER validation by ID."""
        url = (
            f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}"
            f"/ner/groundtruths/{groundtruth_id}/validations/{validation_id}"
        )
        headers = {"Content-Type": "application/json"}
        res = self._perform_request("get", url, headers=headers)
        return self._process_response(res)

    def update_ner_validation_exception(
        self, project_id, groundtruth_id, validation_id, exception_id, resolved
    ):
        """Update the resolved status of a specific NER validation exception.

        :param project_id: ID of the Squirro project.
        :param groundtruth_id: ID of the NER groundtruth.
        :param validation_id: ID of the validation run.
        :param exception_id: ID of the exception to update.
        :param resolved: Boolean indicating whether the exception is resolved.
        :returns: Dictionary containing the response from the API, typically
                  including a success message.
        :raises TypeError: If resolved parameter is not a boolean.
        """
        if not isinstance(resolved, bool):
            raise TypeError(
                f"'resolved' must be a boolean, got {type(resolved).__name__}"
            )
        url = (
            f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}"
            f"/ner/groundtruths/{groundtruth_id}/validations/{validation_id}"
            f"/exceptions/{exception_id}"
        )
        headers = {"Content-Type": "application/json"}
        data = {"resolved": resolved}
        res = self._perform_request("put", url, data=_dumps(data), headers=headers)
        return self._process_response(res)
