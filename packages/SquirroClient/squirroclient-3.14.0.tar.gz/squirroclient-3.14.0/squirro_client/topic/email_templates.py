from ..util import _dumps


class EmailTemplatesMixin:
    def list_email_templates(self):
        """List all email templates.

        :returns: List of email template names.
        """

        url = f"{self.topic_api_url}/v0/{self.tenant}/email_templates"
        headers = {"Content-Type": "application/json"}
        res = self._perform_request("get", url, headers=headers)
        return self._process_response(res, [200])

    def get_email_template(self, template_name):
        """Get an email template.

        :param template_name: str, the name of the template
        :returns: dict
        """

        url = f"{self.topic_api_url}/v0/{self.tenant}/email_templates/{template_name}"
        headers = {"Content-Type": "application/json"}
        res = self._perform_request("get", url, headers=headers)
        return self._process_response(res, [200])

    def edit_email_template(self, template_name, data):
        """Edit an email template.

        :param template_name: str, the name of the template
        :param data: dict, the json body
        """

        url = f"{self.topic_api_url}/v0/{self.tenant}/email_templates/{template_name}"
        headers = {"Content-Type": "application/json"}
        res = self._perform_request("post", url, data=_dumps(data), headers=headers)
        return self._process_response(res, [200])

    def send_sample_email(self, template_name, email, data):
        """Sends a sample email.

        :param template_name: str, the name of the template
        :param email: str, email address
        :param data: dict, with the keys content, content_plain, subject
            providing email templates
        """

        url = f"{self.topic_api_url}/v0/{self.tenant}/email_templates/{template_name}/sample/{email}"
        headers = {"Content-Type": "application/json"}
        res = self._perform_request("post", url, headers=headers, data=_dumps(data))
        return self._process_response(res, [200])
