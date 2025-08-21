import logging
from typing import Any, Optional

from ..util import _dumps

log = logging.getLogger(__name__)


class CommunitiesMixin:
    def get_communities(self, project_id, community_type_id):
        """Return all communities for the given `community_type_id`.

        :param project_id: Project identifier
        :param community_type_id: Community type identifier

        :returns: A list of communities.

        """
        url = f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/community_types/{community_type_id}/communities"
        res = self._perform_request("get", url)
        return self._process_response(res)

    def get_community(
        self, project_id, community_type_id, community_id, verbose=False, query=None
    ):
        """Return a specific community from the given `community_type_id`.

        :param project_id: Project identifier
        :param community_type_id: Community type identifier
        :param community_id: Community identifier
        :param verbose: If set to True, also returns information about the number
                of items and subscriptions in the community, default is False

        :returns: A dictionary of the given community.

        Example::

            >>> client.get_community('BFXfzPHKQP2xRxAP86Kfig',
            ...                      'G0Tm2SQcTqu2d4GvfyrsMg',
            ...                      'yX-D0_oqRgSrCFoTjhmbJg')
            {u'id': u'yX-D0_oqRgSrCFoTjhmbJg',
             u'name': u'Rashford',
             u'created_at': u'2020-09-05T11:21:42',
             u'modified_at': u'2020-09-07T09:33:45',
             u'photo': u'https://twitter.com/MarcusRashford/photo',
             u'facet_value': u'Manchester United',
             }
        """

        if not verbose:
            url = (
                f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/"
                f"community_types/{community_type_id}/communities/{community_id}"
            )
        else:
            url = (
                "{ep}/v0/{tenant}/projects/{project_id}/"
                "community_types/{community_type_id}/communities/{community_id}/detail?query={query}"
            ).format(
                ep=self.topic_api_url,
                tenant=self.tenant,
                project_id=project_id,
                community_type_id=community_type_id,
                community_id=community_id,
                query=query or "",
            )
        res = self._perform_request("get", url)
        return self._process_response(res)

    def get_project_communities(self, project_id):
        """Return all communities for the given `project_id`.

        :param project_id: Project identifier

        :returns: A list of communities.

        """
        url = f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/communities"
        res = self._perform_request("get", url)
        return self._process_response(res)

    def create_community(self, project_id, community_type_id, name, photo, facet_value):
        """Create a new community.

        :param project_id: Project identifier
        :param community_type_id: Community type identifier
        :param name: Name of the community
        :param photo: Address to the photo of the community
        :param facet_value: Value of the facet the community belongs to

        :returns: A dictionary of the created community.

        Example::

            >>> client.create_community(project_id='BFXfzPHKQP2xRxAP86Kfig',
            ...                      community_type_id='G0Tm2SQcTqu2d4GvfyrsMg',
            ...                      name='Rashford',
            ...                      photo='https://twitter.com/MarcusRashford/photo',
            ...                      facet_value='Manchester United')
            {u'id': u'yX-D0_oqRgSrCFoTjhmbJg',
             u'name': u'Rashford',
             u'created_at': u'2020-09-05T11:21:42',
             u'modified_at': u'2020-09-05T11:21:42',
             u'photo': u'https://twitter.com/MarcusRashford/photo',
             u'facet_value': u'Manchester United',
             }
        """

        url = f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/community_types/{community_type_id}/communities"

        data = {"name": name, "photo": photo, "facet_value": facet_value}

        headers = {"Content-Type": "application/json"}
        res = self._perform_request("post", url, data=_dumps(data), headers=headers)
        return self._process_response(res, [201])

    def create_or_update_communities(
        self,
        project_id: str,
        community_type_id: str,
        data: Optional[list[dict[str, Any]]],
        from_facet: Optional[str],
    ):
        """
        Create or update batch of communities.

        Either `data` or `from_facet` must be filled in the request. Both can't
        contain values at the same time. It returns the batch ID which can be used to
        poll for the status of the task.


        :param project_id: Project identifier
        :param community_type_id: Community type identifier
        :param data: Communities data
        :param from_facet: Facet name to create communities based on

        :returns: A dictionary containing batch ID and message about the start of
                creating and updating communities.

        Example::

            >>> client.create_or_update_communities(
            ...                      project_id='BFXfzPHKQP2xRxAP86Kfig',
            ...                      community_type_id='G0Tm2SQcTqu2d4GvfyrsMg',
            ...                      data=[
            ...                             {"name": "Robert Lewandowski", "facet_value": "Robert Lewandowski"},
            ...                             {"name": "Cristiano Ronaldo", "facet_value": "Cristiano Ronaldo"},
            ...                         ]
            ...                      )
            {
                'message': 'Started creating or updating batch of communities for the community type with id "G0Tm2SQcTqu2d4GvfyrsMg"',
                'batch_id': 'a4iqj_ZBTQiRhux_8XnITw',
            }
        """
        url = (
            f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}"
            f"/community_types/{community_type_id}/communities/batch"
        )

        headers = {"Content-Type": "application/json"}
        payload = {"data": data, "from_facet": from_facet}
        res = self._perform_request("post", url, data=_dumps(payload), headers=headers)
        return self._process_response(res, [201])

    def modify_community(
        self,
        project_id,
        community_type_id,
        community_id,
        name=None,
        photo=None,
        facet_value=None,
    ):
        """Modify a community.

        :param project_id: Project identifier
        :param community_type_id: Community type identifier
        :param community_id: The identifier of the community to be modified
        :param name: Name of the community
        :param photo: Address to the photo of the community
        :param facet_value: Value of the facet the community belongs to

        :returns: A dictionary of the modified community.

        Example::

            >>> client.modify_community(project_id='BFXfzPHKQP2xRxAP86Kfig',
            ...                      community_type_id='G0Tm2SQcTqu2d4GvfyrsMg',
            ...                      community_id='yX-D0_oqRgSrCFoTjhmbJg',
            ...                      name='Marcus',
            ...                      photo='https://twitter.com/MarcusRashford/photo',
            ...                      facet_value='Manchester United')
            {u'id': u'yX-D0_oqRgSrCFoTjhmbJg',
             u'name': u'Marcus',
             u'created_at': u'2020-09-05T11:21:42',
             u'modified_at': u'2020-09-05T13:24:40',
             u'photo': u'https://twitter.com/MarcusRashford/photo',
             u'facet_value': u'Manchester United',
             }
        """
        url = (
            f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/"
            f"community_types/{community_type_id}/communities/{community_id}"
        )
        data = {"name": name, "photo": photo, "facet_value": facet_value}

        headers = {"Content-Type": "application/json"}

        put_data = {}
        for key, value in data.items():
            if value is not None:
                put_data[key] = value
        headers = {"Content-Type": "application/json"}
        res = self._perform_request("put", url, data=_dumps(put_data), headers=headers)
        return self._process_response(res)

    def delete_community(self, project_id, community_type_id, community_id):
        """Delete a specific community from the given project.

        :param project_id: Project identifier
        :param community_type_id: Community type identifier
        :param community_id: Community identifier

        :returns: No return value.

        Example::

            >>> client.delete_community('BFXfzPHKQP2xRxAP86Kfig',
            ...                      'G0Tm2SQcTqu2d4GvfyrsMg',
            ...                      'yX-D0_oqRgSrCFoTjhmbJg')
        """
        url = (
            f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/"
            f"community_types/{community_type_id}/communities/{community_id}"
        )
        res = self._perform_request("delete", url)
        return self._process_response(res, [204])

    def get_community_followers(self, project_id, community_type_id, community_id):
        """Return the user details of users subscribed to the community with
        given `community_id`.

        :param project_id: Project identifier
        :param community_type_id: Community type identifier
        :param community_id: Community identifier

        :returns: A list of dictionaries with user details.

        Example::

            >>> client.get_community_followers('BFXfzPHKQP2xRxAP86Kfig',
            ...                      'G0Tm2SQcTqu2d4GvfyrsMg',
            ...                      'yX-D0_oqRgSrCFoTjhmbJg')
            [
                {u'full_name': u'Marcus Rashford',
                u'email': u'rashford@mufc.com',
                },
                .
                .
                .
                {u'full_name': u'David De Gea',
                u'email': u'degea@mufc.com',
                }
            ]
        """

        url = (
            f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/"
            f"community_types/{community_type_id}/communities/{community_id}/followers"
        )
        res = self._perform_request("get", url)
        return self._process_response(res)
