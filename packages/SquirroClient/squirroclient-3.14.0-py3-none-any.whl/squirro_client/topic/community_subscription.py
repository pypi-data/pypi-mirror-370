import logging
from typing import Any, Optional

from ..util import _dumps

log = logging.getLogger(__name__)


class CommunitySubscriptionsMixin:
    def get_community_subscriptions(
        self,
        project_id,
        include_count_of_items=False,
        query: Optional[str] = None,
        start=None,
        count=-1,
        query_context: Optional[dict[str, Any]] = None,
    ):
        """Returns all community subscriptions for a project and a user.

        :param project_id: Project Identifier
        :param include_count_of_items: Boolean argument to include the count of
            items belonging to the subscribed communities of the user.
            Defaults to False.
        :param query: Query to filter community subscriptions.
        :param start: Integer. Used for pagination of objects. If set, the
            objects starting with offset `start` are returned. Defaults to None.
        :param count: Integer. Used for pagination of objects. If set, `count`
            number of communities are returned. To return all communities, set
            to -1. Defaults to -1.
        :param query_context: Dictionary with more context of the user's input / intent:
            - `searchbar_query` : Terms that user typed in a searchbar.
            - `dashboard_filters` : Additional filter-queries provided via dashboard or widget configuration.
            - `community_query` : Selected community in the Community 360 dashboard.
            - `like` : Additional input to perform approximate search on.
                    For now `like` is considered to be a long string (e.g. paragraphs)
            - `parsed` : The parsed, analysed and enriched representation of the `searchbar_query` (response of the configured `query-processing workflow <https://go.squirro.com/libnlp-query-processing>`_)

        Example::

            >>> client.get_community_subscriptions('Xh9CeyQtTYe2cv5F11e6nQ')
            [
                {
                "id": "D0nEBlUmTLqxq6lwZj4rTw",
                "user_id": "-XNqd1bARxuA0L1jh3OeeQ",
                "community_id": "OSACPQKbRz2dadBM4nSseA",
                "created_at": "2020-09-14T09:12:21"
                },
                {
                "id": "QmykmwR3Tb6ZEHI6DJQzUg",
                "user_id": "-XNqd1bARxuA0L1jh3OeeQ",
                "community_id": "mNDkc6q9QvuL8EVMWA3cgg",
                "created_at": "2020-09-14T09:17:15"
                }

            ]

        TODO: allow for specifying user id
        """
        url = f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/community_subscriptions"
        params = {
            "include_count_of_items": include_count_of_items,
            "query": query,
            "start": start,
            "count": count,
        }
        if query_context:
            params["query_context"] = _dumps(query_context)
        res = self._perform_request("get", url, params=params)
        return self._process_response(res)

    def new_community_subscriptions(
        self,
        project_id,
        community_ids,
        remove_existing_subscriptions=False,
        user_id=None,
        include_count_of_items=False,
    ):
        """Creates a new community subscription for a project
        given the community_id

        :param project_id: Project Identifier
        :param community_ids: Ids of the communities to subscribe to
        :param remove_existing_subscriptions: Boolean flag to remove existing subscriptions
        :param user_id: Id of the user subscribing to the community ids
        :param include_count_of_items: Boolean flag to add total count of items for a community subscription

        Example::

            >>> client.new_community_subscription(
                    'Xh9CeyQtTYe2cv5F11e6nQ',
                    ['mNDkc6q9QvuL8EVMWA3cgg','otCTwaF9Qs-66MFGLCtyKQ']
                    remove_existing_subscriptions = True
                )
            {
                "id": "QmykmwR3Tb6ZEHI6DJQzUg",
                "user_id": "-XNqd1bARxuA0L1jh3OeeQ",
                "community_id": "mNDkc6q9QvuL8EVMWA3cgg",
                "created_at": "2020-09-14T09:17:15"
            }
        """

        url = f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/community_subscriptions"
        data = {
            "community_ids": community_ids,
            "remove_existing_subscriptions": remove_existing_subscriptions,
            "user_id": user_id,
            "include_count_of_items": include_count_of_items,
        }

        headers = {"Content-Type": "application/json"}
        res = self._perform_request("post", url, data=_dumps(data), headers=headers)
        return self._process_response(res, [201])

    def delete_community_subscription(self, project_id, subscription_id):
        """Deletes a community subscription

        :param project_id: Project Identifier
        :param subscription_id: Community subscription Identifier

        Example::

            >>> client.delete_community_subscription(
                'Xh9CeyQtTYe2cv5F11e6nQ',
                'mNDkc6q9QvuL8EVMWA3cgg')
            {}
        """
        url = (
            f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/"
            f"community_subscriptions/{subscription_id}"
        )
        res = self._perform_request("delete", url)
        return self._process_response(res, [204])
