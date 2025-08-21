import logging
from typing import Any, Optional

from ..util import _dumps

log = logging.getLogger(__name__)


class CommunityTypesMixin:
    def get_community_types(self, project_id):
        """Returns all community types for a particular project.

        :param project_id: Project Identifier

        Example::

            >>> client.get_community_types('Xh9CeyQtTYe2cv5F11e6nQ')
            [
                {
                "id": "9WArQ7hhRUeEkg3_CLdfLA",
                "created_at": "2020-09-09T15:19:38",
                "modified_at": "2020-09-09T15:19:38",
                "project_id": "Xh9CeyQtTYe2cv5F11e6nQ",
                "name": "Community_type_2",
                "facet": "Country"
                },
                {
                "id": "LB5Q-GmBSbaNvJhUxXfUaA",
                "created_at": "2020-09-09T15:15:42",
                "modified_at": "2020-09-09T15:15:42",
                "project_id": "Xh9CeyQtTYe2cv5F11e6nQ",
                "name": "Community_type_1",
                "facet": "Company"
                }
            ]
        """

        url = f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/community_types"
        res = self._perform_request("get", url)
        return self._process_response(res)

    def get_community_type(
        self,
        project_id,
        community_type_id,
        include_communities=False,
        start=None,
        count=-1,
        community_partial_name=None,
        include_count_of_items=False,
        query_context: Optional[dict[str, Any]] = None,
    ):
        """Returns a community types for a project
        given the community_type_id

        :param project_id: Project Identifier
        :param community_type_id: Community type Identifier
        :param include_communities: Boolean argument to include all the communities
            belonging to the community type with id `community_type_id`. Defaults
            to False.
        :param start: Integer. Used for pagination of objects. If set, the
            objects starting with offset `start` are returned. Defaults to None.
        :param count: Integer. Used for pagination of objects. If set, `count`
            number of communities are returned. To return all communities, set
            to -1. Defaults to -1.
        :param community_partial_name: Argument to filter communities by name.
        :param include_count_of_items: Boolean argument to include the count of
            items belonging to the communities of community type `community_type_id`.
            Defaults to False.
        :param query_context: Dictionary with more context of the user's input / intent:
            - `searchbar_query` : Terms that user typed in a searchbar.
            - `dashboard_filters` : Additional filter-queries provided via dashboard or widget configuration.
            - `community_query` : Selected community in the Community 360 dashboard.
            - `like` : Additional input to perform approximate search on.
                    For now `like` is considered to be a long string (e.g. paragraphs)
            - `parsed` : The parsed, analysed and enriched representation of the `searchbar_query` (response of the configured `query-processing workflow <https://go.squirro.com/libnlp-query-processing>`_)

        Example::

            >>> client.get_community_type(
                'Xh9CeyQtTYe2cv5F11e6nQ',
                'LB5Q-GmBSbaNvJhUxXfUaA'
            )
            {
                "id": "LB5Q-GmBSbaNvJhUxXfUaA",
                "created_at": "2020-09-09T15:15:42",
                "modified_at": "2020-09-09T15:15:42",
                "project_id": "Xh9CeyQtTYe2cv5F11e6nQ",
                "name": "Community_type_1",
                "facet": "Company"
            }
        """

        url = (
            f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/"
            f"community_types/{community_type_id}"
        )
        params = {
            "include_communities": include_communities,
            "start": start,
            "count": count,
            "community_partial_name": community_partial_name,
            "include_count_of_items": include_count_of_items,
        }
        if query_context:
            params["query_context"] = _dumps(query_context)

        res = self._perform_request("get", url, params=params)
        return self._process_response(res)

    def new_community_type(self, project_id, name, facet=None, photo=None):
        """Creates a new community type

        :param project_id: Project Identifier
        :param name: community type name
        :param facet: facet name associated with the community
        :param photo: Address to the photo of the community

        Example::

            >>> client.new_community_type(
                    'Xh9CeyQtTYe2cv5F11e6nQ',
                    'Community_type_1',
                    facet='Company',
                    photo='https://twitter.com/MarcusRashford/photo',
                    )
            {
                "id": "LB5Q-GmBSbaNvJhUxXfUaA",
                "created_at": "2020-09-09T15:15:42",
                "modified_at": "2020-09-09T15:15:42",
                "project_id": "Xh9CeyQtTYe2cv5F11e6nQ",
                "name": "Community_type_1",
                "facet": "Company",
                "photo": "https://twitter.com/MarcusRashford/photo",
            }
        """

        url = (
            f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/"
            "community_types"
        )
        data = {"name": name}
        if facet:
            data["facet"] = facet
        if photo:
            data["photo"] = photo

        headers = {"Content-Type": "application/json"}
        res = self._perform_request("post", url, data=_dumps(data), headers=headers)
        return self._process_response(res, [201])

    def modify_community_type(self, project_id, community_type_id, name, facet=None):
        """Modifies a community type

        :param project_id: Project Identifier
        :param community_type_id: Community type Identifier
        :param name: community type name
        :param facet: facet name associated with the community

        Example::

            >>> client.modify_community_type(
                    'Xh9CeyQtTYe2cv5F11e6nQ',
                    'LB5Q-GmBSbaNvJhUxXfUaA',
                    'Community_type_1',
                    facet='Country',
                )
            {
                "id": "LB5Q-GmBSbaNvJhUxXfUaA",
                "created_at": "2020-09-09T15:15:42",
                "modified_at": "2020-09-09T15:15:42",
                "project_id": "Xh9CeyQtTYe2cv5F11e6nQ",
                "name": "Community_type_1",
                "facet": "Country"
            }
        """

        url = (
            f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/"
            f"community_types/{community_type_id}"
        )
        data = {"name": name}
        if facet:
            data["facet"] = facet

        headers = {"Content-Type": "application/json"}
        res = self._perform_request("put", url, data=_dumps(data), headers=headers)
        return self._process_response(res)

    def move_community_type(self, project_id, community_type_id, after):
        """Move a community type.

        :param project_id: Project identifier
        :param community_type_id: Community type identifier
        :param after: The community type identifier after which the community
            type should be moved. Can be `None` to move the community type to
            the beginning of the list.

        :returns: No return value.

        Example::

            >>> client.move_community_type('Xh9CeyQtTYe2cv5F11e6nQ',
            ...                            'LB5Q-GmBSbaNvJhUxXfUaA',
            ...                            'AaUfXUhJvNabSBBmG-Q5LB')
        """
        url = (
            f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/"
            f"community_types/{community_type_id}/move"
        )
        headers = {"Content-Type": "application/json"}
        res = self._perform_request(
            "post", url, data=_dumps({"after": after}), headers=headers
        )
        return self._process_response(res, [204])

    def delete_community_type(self, project_id, community_type_id):
        """Deletes a community type

        :param project_id: Project Identifier
        :param community_type_id: Community type Identifier

        Example::

            >>> client.delete_community_type(
                    'Xh9CeyQtTYe2cv5F11e6nQ',
                    'LB5Q-GmBSbaNvJhUxXfUaA')
            {}
        """

        url = (
            f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/"
            f"community_types/{community_type_id}"
        )
        res = self._perform_request("delete", url)
        return self._process_response(res, [204])
