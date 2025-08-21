import logging
from typing import Optional

from ..util import _dumps

log = logging.getLogger(__name__)


class ExecutionError(Exception):
    """Error in executing a machine learning job"""

    pass


class MLModelsMixin:
    #
    #  ML Model
    #
    def get_ml_models(self, project_id):
        """Return all ML Models for a project.

        :param project_id: Id of the Squirro project.
        """
        url = f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/ml_model"
        headers = {"Content-Type": "application/json"}
        res = self._perform_request("get", url, headers=headers)
        return self._process_response(res)["models"]

    def get_ml_model(self, project_id, model_id):
        """Return a single ML Model.

        :param project_id: Id of the Squirro project.
        :param model_id: id of the ML model
        """
        url = f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/ml_model/{model_id}"

        headers = {"Content-Type": "application/json"}
        res = self._perform_request("get", url, headers=headers)
        return self._process_response(res)

    def new_ml_model(
        self,
        project_id,
        name,
        template_id,
        ground_truth_id,
        template_params=None,
        ground_truth_version=None,
        is_incomplete=False,
    ):
        """Create a new ML Model.

        :param project_id: Id of the Squirro project.
        :param name: Name of the ML Model.
        :param template_id: template do be used.
        :param template_params: parameters to initialize the template.
        :param ground_truth_id: id of the grountruth.
        :param ground_truth_version: version of the grountruth if any.
        :param is_incomplete: mark a model as incomplete.
        """

        url = f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/ml_model"
        headers = {"Content-Type": "application/json"}
        # TODO workaround to also allow incomplete models
        model_params = {
            "name": name,
            "template_id": template_id,
            "gt_id": ground_truth_id,
            "template_params": template_params,
            "ground_truth_version": ground_truth_version,
            "is_incomplete": is_incomplete,
        }

        res = self._perform_request(
            "post", url, data=_dumps(model_params), headers=headers
        )
        return self._process_response(res, [201])

    def modify_ml_model(
        self,
        project_id,
        model_id,
        name,
        template_id=None,
        template_params=None,
        ground_truth_id=None,
        ground_truth_version=None,
        is_incomplete=None,
    ):
        """Update ML Model

        :param project_id: Id of the Squirro project.
        :param model_id: Id of the Machine Learning workflow.
        :param name: Name of the ML Model.
        :param template_id: template do be used.
        :param template_params: parameters to initialize the template.
        :param ground_truth_id: id of the groundtruth.
        :param ground_truth_version: version of the groundtruth if any
        :param is_incomplete: mark a model as incomplete.
        """
        url = f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/ml_model/{model_id}"
        headers = {"Content-Type": "application/json"}
        # TODO workaround to also allow incomplete models
        model_params = {
            "name": name,
            "template_id": template_id,
            "gt_id": ground_truth_id,
            "template_params": template_params,
            "ground_truth_version": ground_truth_version,
            "is_incomplete": is_incomplete,
        }
        res = self._perform_request(
            "put", url, data=_dumps(model_params), headers=headers
        )
        return self._process_response(res, [204])

    def delete_ml_model(self, project_id, model_id):
        """Delete ML Model

        :param project_id: Id of the Squirro project.
        :param model_id: Id of the  ML Model.
        """
        url = f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/ml_model/{model_id}"

        headers = {"Content-Type": "application/json"}
        res = self._perform_request("delete", url, headers=headers)
        return self._process_response(res, [204])

    def get_bulk_labeling(
        self,
        project_id,
        groundtruth_id,
        ml_workflow_fields: Optional[list[str]] = None,
        ml_job_fields: Optional[list[str]] = None,
        job_count: Optional[int] = None,
    ):
        """Get new bulk labeling status.

        :param project_id: Id of the Squirro project.
        :param groundtruth_id: id of the grountruth.
        :param ml_workflow_fields: list of fields of ML workflows
        :param ml_job_fields: list of fields of ML jobs
        """

        url = f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/bulk_labeling/{groundtruth_id}"
        headers = {"Content-Type": "application/json"}

        params = {
            "ml_workflow_fields": ml_workflow_fields,
            "ml_job_fields": ml_job_fields,
            "job_count": job_count,
        }

        res = self._perform_request("get", url, data=_dumps(params), headers=headers)
        return self._process_response(res, [200])

    def new_bulk_labeling(
        self,
        project_id,
        groundtruth_id,
        name,
        template_id,
        template_params=None,
    ):
        """Create new bulk labeling.

        :param project_id: Id of the Squirro project.
        :param groundtruth_id: id of the grountruth.
        :param name: Name of the ML Model.
        :param template_id: template do be used.
        :param template_params: parameters to initialize the template.
        """

        url = f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/bulk_labeling/{groundtruth_id}"
        headers = {"Content-Type": "application/json"}

        params = {
            "name": name,
            "template_id": template_id,
            "template_params": template_params,
        }

        res = self._perform_request("post", url, data=_dumps(params), headers=headers)
        return self._process_response(res, [201])
