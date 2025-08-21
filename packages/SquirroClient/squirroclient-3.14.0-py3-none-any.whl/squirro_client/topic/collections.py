import logging
from typing import TYPE_CHECKING, Any, Callable

from pydantic import TypeAdapter
from typing_extensions import TypedDict

from ..util import _dumps

log = logging.getLogger(__name__)


class Collection(TypedDict):
    """Expected format of a collection."""

    id: str
    project_id: str
    name: str
    user_id: str
    item_ids: list[str]


class CollectionsMixin:
    """
    Mixin for collection related API calls.

    Collection is a list of items that can be used to filter the search results.
    """

    if TYPE_CHECKING:
        topic_api_url: str
        tenant: str
        _perform_request: Callable
        _process_response: Callable

    def get_collections(self, project_id: str):
        """Get item collections for a project."""
        url = f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/collections"

        res = self._perform_request("get", url)
        collections = self._process_response(res)
        return TypeAdapter(list[Collection]).validate_python(collections)

    def create_collection(
        self,
        project_id: str,
        name: str,
    ):
        """Create a new collection for a project."""
        data = {
            "name": name,
        }

        url = f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/collections"

        res = self._perform_request("post", url, json=data)
        collection = self._process_response(res, [201])

        return TypeAdapter(Collection).validate_python(collection)

    def get_collection(self, project_id: str, collection_id: str):
        """Get a collection by ID."""
        url = f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/collections/{collection_id}"

        res = self._perform_request("get", url)
        collection = self._process_response(res)

        return TypeAdapter(Collection).validate_python(collection)

    def update_collection(self, project_id: str, collection_id: str, name: str):
        """Update a collection by ID."""
        data = {"name": name}

        headers = {"Content-Type": "application/json"}

        url = f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/collections/{collection_id}"

        res = self._perform_request("put", url, data=_dumps(data), headers=headers)
        collection = self._process_response(res)

        return TypeAdapter(Collection).validate_python(collection)

    def delete_collection(self, project_id: str, collection_id: str) -> dict[Any, Any]:
        """Delete a collection by ID. If successful, returns an empty dictionary."""
        url = f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/collections/{collection_id}"

        res = self._perform_request("delete", url)
        return self._process_response(res, [204])

    def add_item_to_collection(
        self, project_id: str, collection_id: str, item_id: str
    ) -> dict[Any, Any]:
        """Add an item to a collection. The item_id validity is not checked. If successful, returns an empty dictionary."""
        data = {"item_id": item_id}

        headers = {"Content-Type": "application/json"}

        url = f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/collections/{collection_id}/items"

        res = self._perform_request("post", url, data=_dumps(data), headers=headers)
        return self._process_response(res, [204])

    def delete_item_from_collection(
        self, project_id: str, collection_id: str, item_id: str
    ) -> dict[Any, Any]:
        """Delete an item from a collection. If successful, returns an empty dictionary."""
        url = f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/collections/{collection_id}/items/{item_id}"

        res = self._perform_request("delete", url)
        return self._process_response(res, [204])

    def get_collections_containing_items(self, project_id: str, item_ids: list[str]):
        """Get collections that contain the given items. Returns a dictionary with item IDs as keys and list of collection IDs as values."""
        data = {"item_ids": item_ids}

        headers = {"Content-Type": "application/json"}

        url = f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/item-collections"

        res = self._perform_request("post", url, data=_dumps(data), headers=headers)

        items_to_collections = self._process_response(res)

        return TypeAdapter(dict[str, list[str]]).validate_python(items_to_collections)
