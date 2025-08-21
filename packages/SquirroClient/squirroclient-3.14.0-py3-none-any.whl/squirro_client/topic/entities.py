from ..util import _dumps


class EntitiesMixin:
    def create_entities(self, project_id, entity_list):
        """Creates new entities.

        :param entity_list: [entity, ...]
        """

        url = f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/entities"
        headers = {"Content-Type": "application/json"}
        res = self._perform_request(
            "post", url, data=_dumps(entity_list), headers=headers
        )
        return self._process_response(res, [201])

    def modify_entities(self, project_id, entity_list):
        """Updates existing entities.

        :param entity_list: [entity, ...]
        """

        url = f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/entities"
        headers = {"Content-Type": "application/json"}
        res = self._perform_request(
            "put", url, data=_dumps(entity_list), headers=headers
        )
        return self._process_response(res, [204])

    def get_entities(self, project_id, entity_ids):
        """Gets entities by entity ids.

        :param entity_ids: List of IDs referring to entities
        """

        url = f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/entities"
        entity_ids = ",".join(entity_ids)
        res = self._perform_request("get", url, params=dict(ids=entity_ids))
        return self._process_response(res)

    def delete_entities(self, project_id, entity_ids):
        """Deletes entities by entity ids.

        :param entity_ids: List of IDs referring to entities
        """

        url = f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/entities"
        entity_ids = ",".join(entity_ids)
        res = self._perform_request("delete", url, params=dict(ids=entity_ids))
        return self._process_response(res, [204])

    def get_entities_properties(self, project_id, query=None):
        """Get entity types and corresponding properties of entity

        :param project_id: Identifier of project
        :param query: Filtering query
        :return: Dictionary of entity and corresponding properties of entity

        Example::

            {
                "career": ["properties.job,numeric_properties.salary"],
            }

        """

        url = (
            f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/entities"
            "/properties"
        )
        res = self._perform_request("get", url, params=dict(query=query))
        return self._process_response(res)
