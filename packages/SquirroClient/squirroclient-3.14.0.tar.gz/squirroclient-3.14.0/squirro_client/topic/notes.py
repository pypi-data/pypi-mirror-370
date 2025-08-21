from typing import Optional

from ..util import _dumps


class NotesMixin:
    """Notes API"""

    def create_note(
        self,
        project_id: str,
        item_id: str,
        clip: dict,
        color: Optional[str] = None,
        comment: Optional[str] = None,
        communities: Optional[list[dict]] = None,
        facets: Optional[list[dict]] = None,
    ):
        """Create a new Note.

        :param project_id: the ID of the project in which the note will be created.
        :param item_id: the ID of the Squirro Item for which the note is created.
        :param clip: a dict which contains the information to locate the selected
            passage for the note. If it is a document-level note (i.e., a note for the
            whole item, not for a specific part of it), then only the `field` key with
            value `item` needs to be supplied.
        :param color: the color to use to highlight the note (selected text passage) on
            the UI.
        :param comment: an initial comment along with the creation of the note.
        :param communities: a list of communities assigned to the note.
        :param facets: a list of facets assigned to the note.
        """
        headers = {"Content-Type": "application/json"}

        data = {"item_id": item_id, "clip": clip}

        if color is not None:
            data["color"] = color

        if comment is not None:
            data["comment"] = comment

        if communities is not None:
            data["communities"] = communities

        if facets is not None:
            data["facets"] = facets

        url = f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/notes"

        res = self._perform_request("post", url, data=_dumps(data), headers=headers)

        return self._process_response(res, [201])

    def edit_note(
        self,
        project_id: str,
        note_id: str,
        color: Optional[str] = None,
        communities: Optional[list[dict]] = None,
        facets: Optional[list[dict]] = None,
    ):
        """Edit the Note.

        :param project_id: the ID of the project that the note belongs to.
        :param note_id: the ID of the Note which will be edited.
        :param color: the color to use to highlight the note (selected text passage) on
            the UI.
        :param communities: a list of communities assigned to the note.
        :param facets: a list of facets assigned to the note.
        """
        headers = {"Content-Type": "application/json"}

        data = {}

        if color is not None:
            data["color"] = color

        if communities is not None:
            data["communities"] = communities

        if facets is not None:
            data["facets"] = facets

        url = f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/notes/{note_id}"

        res = self._perform_request("put", url, data=_dumps(data), headers=headers)

        return self._process_response(res, [200])

    def delete_note(self, project_id: str, note_id: str):
        """Delete an existing Note.

        :param project_id: the ID of the project that the note belongs to.
        :param note_id: the ID of the Note which will be deleted.
        """
        url = f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/notes/{note_id}"
        res = self._perform_request("delete", url)
        return self._process_response(res, [204])

    def create_note_comment(
        self,
        project_id: str,
        note_id: str,
        text: str,
    ):
        """Create a new Comment for the Note.

        :param project_id: the ID of the project in which the note will be created.
        :param note_id: the ID of the Note for which the comment is created.
        :param text: a text of the comment.
        """
        headers = {"Content-Type": "application/json"}

        data = {"text": text}

        url = f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/notes/{note_id}/comments"

        res = self._perform_request("post", url, data=_dumps(data), headers=headers)

        return self._process_response(res, [201])

    def edit_note_comment(
        self,
        project_id: str,
        note_id: str,
        comment_id: str,
        text: str,
    ):
        """Edit the Comment of the Note.

        :param project_id: the ID of the project in which the note will be edited.
        :param note_id: the ID of the Note of the Comment.
        :param comment_id: the ID of the Comment.
        :param text: a new text of the Comment.
        """
        headers = {"Content-Type": "application/json"}

        data = {"text": text}

        url = f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/notes/{note_id}/comments/{comment_id}"

        res = self._perform_request("put", url, data=_dumps(data), headers=headers)

        return self._process_response(res, [200])

    def delete_note_comment(
        self,
        project_id: str,
        note_id: str,
        comment_id: str,
    ):
        """Delete the Comment of the Note.

        :param project_id: ID of the project that owns the note for which the comment will be deleted.
        :param note_id: the ID of the Note  of the Comment.
        :param comment_id: the ID of the Comment.
        """

        url = f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/notes/{note_id}/comments/{comment_id}"

        res = self._perform_request("delete", url)

        return self._process_response(res, [200])

    def query_notes(
        self,
        project_id: str,
        query: Optional[str] = None,
        group_by_item: bool = False,
        item_fields: Optional[str] = None,
    ):
        """
        :param project_id: the ID of the project from which notes will be queried.
        :param query: Squirro syntax query to run against notes. Only notes that match
            the given search criteria will be returned.
        :param group_by_item: whether in the response the notes are grouped by the item
            they belong. Certain item fields can be requested when this is enabled.
        :param item_fields: comma-separated list of item fields to return. It is only
            applicable when the `group_by_item` parameter is `True`.
        """
        headers = {"Content-Type": "application/json"}

        data = {"group_by_item": group_by_item}

        if query is not None:
            data["query"] = query

        if group_by_item and item_fields is not None:
            data["item_fields"] = item_fields

        url = f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/notes/query"

        res = self._perform_request("post", url, data=_dumps(data), headers=headers)

        return self._process_response(res, [200])
