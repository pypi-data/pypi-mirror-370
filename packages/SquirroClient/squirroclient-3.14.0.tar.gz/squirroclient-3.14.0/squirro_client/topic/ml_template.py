import logging

from ..util import _dumps

log = logging.getLogger(__name__)


class ExecutionError(Exception):
    """Error in executing a machine learning job"""

    pass


class MLTemplatesMixin:
    #
    #  ML Templates
    #
    def get_templates(self, project_id, groundtruth_id=None):
        """Return all available Templates.

        :param project_id: Id of the Squirro project.
        :param groundtruth_id: Id of the Ground Truth (for enriching template with
                               default values).
        """
        url = f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/ml_template"

        headers = {"Content-Type": "application/json"}

        data = {"groundtruth_id": groundtruth_id}
        res = self._perform_request("get", url, headers=headers, params=data)
        return self._process_response(res)

    def get_template(self, project_id, template_id, groundtruth_id=None):
        """Returns a single Template

        :param project_id: Id of the Squirro project.
        :param template_id: Id of the machine learning Template.
        :param groundtruth_id: Id of the Ground Truth (for enriching template with
                               default values).
        :return:
        """
        url = f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/ml_template/{template_id}"

        headers = {"Content-Type": "application/json"}
        data = {"groundtruth_id": groundtruth_id}

        res = self._process_response(
            self._perform_request("get", url, headers=headers, params=data)
        )
        return res["template"]

    def generate_workflows(self, project_id, template_id, params={}):
        """Generate a new template.

        :param project_id: Id of the Squirro project.
        :param template_id: id of the template.
        :param params: dictionary that contains the parameters for the template.
        """

        url = f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/ml_template/{template_id}"

        headers = {"Content-Type": "application/json"}

        res = self._perform_request("post", url, data=_dumps(params), headers=headers)

        return self._process_response(res, [200])
