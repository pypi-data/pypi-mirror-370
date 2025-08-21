import datetime
import logging

from ..util import _dumps

log = logging.getLogger(__name__)


class ExecutionError(Exception):
    """Error in executing a machine learning job"""

    pass


class MLGroundTruthMixin:
    #
    #  ML Groundtruth (GT)
    #
    def get_groundtruths(self, project_id):
        """Return all ground truth for a project in a list.

        :param project_id: Id of the Squirro project.
        """

        base_url = "{}/v0/{}/projects/{}/groundtruths"
        url = base_url.format(self.topic_api_url, self.tenant, project_id)

        headers = {"Content-Type": "application/json"}
        res = self._perform_request("get", url, headers=headers)
        return self._process_response(res)

    def get_groundtruth(self, project_id, groundtruth_id):
        """Get a single Ground Truth.

        :param project_id: Id of the Squirro project.
        :param groundtruth_id: Id of the GroundTruth

        **Examples**

        *Get a single groundtruth*::

            >>> client.get_groundtruth(
                        project_id="DSuNrcnlSc6x5SJZh02IyQ",
                        groundtruth_id="n57sJlpcTLy4_XxdvHvx5g")
            {'bulk_labeling_status': 'no bulk labelings',
            'config': {'candidatesets': [], 'labels': ['yes', 'no']},
            'created_at': '1996-03-13T00:00:00',
            'id': 'n57sJlpcTLy4_XxdvHvx5g',
            'modified_at': '2015-06-09T00:00:00',
            'name': 'Commercial final fly share white focus voice.',
            'project_id': 'DSuNrcnlSc6x5SJZh02IyQ',
            'bulk_labeling_status': 'no bulk labelings'
            'rules': {}}
        """
        base_url = "{}/v0/{}/projects/{}/groundtruths/{}"
        headers = {"Content-Type": "application/json"}

        url = base_url.format(
            self.topic_api_url, self.tenant, project_id, groundtruth_id
        )
        res = self._perform_request("get", url, headers=headers)
        return self._process_response(res)

    def new_groundtruth(self, project_id, name, config):
        """Create a new Ground Truth.

        :param project_id: Id of the Squirro project.
        :param name: Name of the Ground Truth.
        :param config: Ground Truth Config.
        """

        base_url = "{}/v0/{}/projects/{}/groundtruths"
        headers = {"Content-Type": "application/json"}

        url = base_url.format(self.topic_api_url, self.tenant, project_id)

        groundtruth_params = {"name": name, "config": config}

        res = self._perform_request(
            "post", url, data=_dumps(groundtruth_params), headers=headers
        )
        return self._process_response(res, [201])

    def modify_groundtruth(self, project_id, groundtruth_id, name=None, config=None):
        """Modify an existing Ground Truth.

        :param project_id: Id of the Squirro project.
        :param groundtruth_id: Id of the Ground Truth.
        :param name: Name of the Ground Truth.
        :param config: Dictionary of Ground Truth config.
        """
        url = "{}/v0/{}/projects/{}/groundtruths/{}"
        headers = {"Content-Type": "application/json"}

        groundtruth_update = {}

        if name is not None:
            groundtruth_update["name"] = name
        if config is not None:
            groundtruth_update["config"] = config

        url = url.format(self.topic_api_url, self.tenant, project_id, groundtruth_id)
        res = self._perform_request(
            "put", url, data=_dumps(groundtruth_update), headers=headers
        )
        return self._process_response(res, [204])

    def delete_groundtruth(self, project_id, groundtruth_id):
        """Delete Ground Truth

        :param project_id: Id of the Squirro project.
        :param groundtruth_id: Id of the Ground Truth.
        """
        url = "{}/v0/{}/projects/{}/groundtruths/{}"
        headers = {"Content-Type": "application/json"}

        url = url.format(self.topic_api_url, self.tenant, project_id, groundtruth_id)
        res = self._perform_request("delete", url, headers=headers)
        return self._process_response(res, [204])

    #
    #  ML Ground Truth Label
    #
    def get_groundtruth_labels(
        self,
        project_id,
        groundtruth_id,
        user_id=None,
        temporal_version=None,
        label=None,
        extract_query=None,
        item_ids=[],
        count=None,
        start=None,
    ):
        """Return the labeled extract of a ground truth for a project in a list. Note: to avoid timeout issues in large ground truths, use `get_groundtruth_labels_batched` instead.

        :param project_id: Id of the Squirro project.
        :param groundtruth_id: Id of the GroundTruth
        :param user_id: Id of the user to filter Ground Truth by
        :param temporal_version: temporal version of the Ground Truth
        :param label: label to filter Ground Truth by
        :param: item_ids: item_ids to filter Ground Truth by
        :param: count: num of elements to retrieve of the Ground Truth
        :param: start: pagination offset for the retrieval of the Ground Truth
        """
        base_url = "{}/v0/{}/projects/{}/groundtruths/{}/labels"
        headers = {"Content-Type": "application/json"}
        data = {
            "user_id": user_id,
            "temporal_version": temporal_version,
            "label": label,
            "extract_query": extract_query,
            "item_ids": ",".join(item_ids),
            "count": count,
            "start": start,
        }
        url = base_url.format(
            self.topic_api_url, self.tenant, project_id, groundtruth_id
        )
        res = self._perform_request("get", url, headers=headers, params=data)
        return self._process_response(res)

    def get_groundtruth_labels_batched(
        self,
        project_id: str,
        groundtruth_id: str,
        batch_size=1000,
        temporal_version=None,
    ):
        """
        Returns a generator that goes through all the valid labeled extracts from the provided groundtruth. The generator is only valid for a short period of time, as it uses Elasticsearch's PIT API under the hood. It is preferable to use this method instead of `get_groundtruth_labels` when the number of labels is large, as it avoids timeout issues.

        Args:
            project_id (str): The ID of the project.
            groundtruth_id (str): The ID of the groundtruth.
            batch_size (int, optional): The size of the batch requested to the API. Defaults to 1000. If time out issues are encountered, try to reduce this value.
            temporal_version (str, optional): The datetime string corresponding to the Ground Truth temporal version. Defaults to None.

        Yields:
            dict: A dictionary containing information about a labeled extract, including the extract text, keywords, item ID, etc.
        """
        headers = {"Content-Type": "application/json"}
        data = {
            "batch_size": batch_size,
            "temporal_version": temporal_version,
        }

        url = f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/groundtruths/{groundtruth_id}/labels_batch"

        labels = True
        res = None
        try:
            while labels:
                res = self._process_response(
                    self._perform_request(
                        "post", url, data=_dumps(data), headers=headers
                    )
                )

                res = res.get("groundtruth_labels", {})

                labels = res.get("labels", [])
                yield from labels
                if not res.get("eof"):
                    data["pit_id"] = res["next_params"]["pit_id"]
                    data["search_after"] = res["next_params"]["search_after"]
                else:
                    break
        except GeneratorExit:
            logging.warning("Scanning of items was interrupted")
        except Exception as ex:
            logging.exception(f"Could not process the response: {ex}")
            raise
        finally:
            if res is not None:
                pit_id = res.get("next_params").get("pit_id")
                url = (
                    f"{self.topic_api_url}/{self.version}/{self.tenant}/"
                    f"projects/{project_id}/scan_artifacts/pit_context/{pit_id}"
                )
                res = self._perform_request("delete", url)

    def get_groundtruth_label(self, project_id, groundtruth_id, label_id):
        """Get a single labeled extract from a Ground Truth.

        :param project_id: Id of the Squirro project.
        :param groundtruth_id: Id of the GroundTruth
        :param label_id: Id of the labeled extract
        """
        base_url = "{}/v0/{}/projects/{}/groundtruths/{}/labels/{}/"
        headers = {"Content-Type": "application/json"}

        url = base_url.format(
            self.topic_api_url, self.tenant, project_id, groundtruth_id, label_id
        )
        res = self._perform_request("get", url, headers=headers)
        return self._process_response(res)

    def new_groundtruth_label(self, project_id, groundtruth_id, label):
        """Create a new labeled extract.

        :param project_id: Id of the Squirro project.
        :param groundtruth_id: Id of the Ground Truth
        :param label: information of the labeled extract.
        """

        base_url = "{}/v0/{}/projects/{}/groundtruths/{}/labels"
        headers = {"Content-Type": "application/json"}

        url = base_url.format(
            self.topic_api_url, self.tenant, project_id, groundtruth_id
        )

        label_params = {"label": label}

        res = self._perform_request(
            "post", url, data=_dumps(label_params), headers=headers
        )
        return self._process_response(res, [201])

    def new_groundtruth_labels(self, project_id, groundtruth_id, labels):
        """
        Create multiple labeled extracts.

        :param project_id: Id of the Squirro project.
        :param groundtruth_id: Id of the Ground Truth.
        :param labels: list of dicts, where each dict contains information of a labeled
                       extract.
        """
        base_url = "{}/v0/{}/projects/{}/groundtruths/{}/labels_bulk"
        headers = {"Content-Type": "application/json"}

        url = base_url.format(
            self.topic_api_url, self.tenant, project_id, groundtruth_id
        )

        params = {"labels": labels}

        res = self._perform_request("post", url, data=_dumps(params), headers=headers)
        return self._process_response(res, [201])

    def modify_groundtruth_label(
        self, project_id, groundtruth_id, label_id, validity, label=None
    ):
        """Modify an existing labeled extract.

        :param project_id: Id of the Squirro project
        :param groundtruth_id: Id of the Ground Truth
        :param label_id: Id of the labeled extract
        :param validity: validity of the labeled extract
        :param label: label of the labeled extract
        """
        base_url = "{}/v0/{}/projects/{}/groundtruths/{}/labels"
        headers = {"Content-Type": "application/json"}

        label_update = {"validity": validity, "label": label}

        url = "/".join([base_url, label_id])
        url = url.format(self.topic_api_url, self.tenant, project_id, groundtruth_id)
        res = self._perform_request(
            "put", url, data=_dumps(label_update), headers=headers
        )
        return self._process_response(res, [200, 201])

    def delete_groundtruth_label(self, project_id, groundtruth_id, label_id):
        """Delete labeled extract

        :param project_id: Id of the Squirro project.
        :param groundtruth_id: Id of the Ground Truth.
        :param label_id: Id of the labeled extract
        """
        base_url = "{}/v0/{}/projects/{}/groundtruths/{}/labels"
        headers = {"Content-Type": "application/json"}

        url = "/".join([base_url, label_id])
        url = url.format(self.topic_api_url, self.tenant, project_id, groundtruth_id)
        res = self._perform_request("delete", url, headers=headers)
        return self._process_response(res, [204])

    #
    #  ML Ground Truth Rule
    #
    def get_groundtruth_rules(self, project_id, groundtruth_id):
        """Get all rules for the Ground Truth.

        :param project_id: Id of the Squirro project
        :param groundtruth_id: Id of the GroundTruth
        """
        base_url = "{}/v0/{}/projects/{}/groundtruths/{}/rules"
        headers = {"Content-Type": "application/json"}

        url = base_url.format(
            self.topic_api_url, self.tenant, project_id, groundtruth_id
        )
        res = self._perform_request("get", url, headers=headers)
        return self._process_response(res)

    def get_groundtruth_rule(self, project_id, groundtruth_id, rule_id):
        """Get a single rule of the Ground Truth.

        :param project_id: Id of the Squirro project.
        :param groundtruth_id: Id of the GroundTruth
        :param rule_id: Id of the rule
        """
        base_url = "{}/v0/{}/projects/{}/groundtruths/{}/rules/{}"
        headers = {"Content-Type": "application/json"}

        url = base_url.format(
            self.topic_api_url, self.tenant, project_id, groundtruth_id, rule_id
        )
        res = self._perform_request("get", url, headers=headers)
        return self._process_response(res)

    def new_groundtruth_rule(self, project_id, groundtruth_id, rule):
        """Create a new rule in Ground Truth.

        :param project_id: Id of the Squirro project.
        :param groundtruth_id: Id of the Ground Truth
        :param rule: information of the rule.
        """

        base_url = "{}/v0/{}/projects/{}/groundtruths/{}/rules"
        headers = {"Content-Type": "application/json"}

        url = base_url.format(
            self.topic_api_url, self.tenant, project_id, groundtruth_id
        )

        rule_params = {"rule": rule}

        res = self._perform_request(
            "post", url, data=_dumps(rule_params), headers=headers
        )
        return self._process_response(res, [201])

    def modify_groundtruth_rule(self, project_id, groundtruth_id, rule_id, rule):
        """Modify an existing rule.

        :param project_id: Id of the Squirro project.
        :param groundtruth_id: Id of the Ground Truth.
        :param rule_id: Id of the rule
        :param rule: information of the rule.
        """
        base_url = "{}/v0/{}/projects/{}/groundtruths/{}/rules"
        headers = {"Content-Type": "application/json"}

        rule_update = {"rule": rule}

        url = "/".join([base_url, rule_id])
        url = url.format(self.topic_api_url, self.tenant, project_id, groundtruth_id)
        res = self._perform_request(
            "put", url, data=_dumps(rule_update), headers=headers
        )
        return self._process_response(res, [204])

    def delete_groundtruth_rule(self, project_id, groundtruth_id, rule_id):
        """Delete rule

        :param project_id: Id of the Squirro project.
        :param groundtruth_id: Id of the Ground Truth.
        :param rule_id: Id of the rule
        """
        base_url = "{}/v0/{}/projects/{}/groundtruths/{}/rules"
        headers = {"Content-Type": "application/json"}

        url = "/".join([base_url, rule_id])
        url = url.format(self.topic_api_url, self.tenant, project_id, groundtruth_id)
        res = self._perform_request("delete", url, headers=headers)
        return self._process_response(res, [204])

    #
    #  Ground Truth Item
    #
    def get_groundtruth_items(
        self,
        project_id,
        groundtruth_id,
        user_id=None,
        temporal_version=None,
        label=None,
        labelled_filter=None,
        highlight_filter=False,
        **kwargs,
    ):
        """Returns items for the provided project enriched with Ground Truth data.

        :param project_id: Id of the Squirro project
        :param groundtruth_id: Id of the GroundTruth
        :param user_id: Id of the user to filter Ground Truth by
        :param temporal_version: temporal version of the Ground Truth
        :param label: label to filter Ground Truth by
        :param labelled_filter: filter if all items, only the already labelled or only the unlabelled items should get returned (accepted values:'all','labelled' and 'not_labelled')
        :param highlight_filter : filter if only the highlighted items should get returned
        :param kwargs: Additional query parameters. All keyword arguments are
                       passed on verbatim to the API.
        :return:
        """
        base_url = "{}/v0/{}/projects/{}/groundtruths/{}/items"
        headers = {"Content-Type": "application/json"}
        data = {
            "user_id": user_id,
            "temporal_version": temporal_version,
            "label": label,
            "labelled_filter": labelled_filter,
            "highlight_filter": highlight_filter,
        }
        data.update(**kwargs)
        url = base_url.format(
            self.topic_api_url, self.tenant, project_id, groundtruth_id
        )
        res = self._perform_request("get", url, headers=headers, params=data)
        return self._process_response(res)

    def get_groundtruth_item(
        self,
        project_id,
        groundtruth_id,
        item_id,
        highlight_query="",
        user_id=None,
        temporal_version=datetime.datetime.utcnow().isoformat(),
        label=None,
        include_sentences=False,
    ):
        """Returns a item of the provided project enriched with Ground Truth data.

        :param project_id: Id of the Squirro project
        :param groundtruth_id: Id of the GroundTruth
        :param item_id: Id of the item
        :param highlight_query: query containing highlight information
        :param user_id: Id of the user to filter Ground Truth by
        :param temporal_version: Temporal version of the Ground Truth
        :param label: Label tag to filter Ground Truth by
        :param include_sentences: Flag to return documents split in sentences
        :return:
        """
        base_url = "{}/v0/{}/projects/{}/groundtruths/{}/items/{}"
        headers = {"Content-Type": "application/json"}

        data = _dumps(
            {
                "data": {
                    "highlight_query": highlight_query,
                    "label": label,
                    "user_id": user_id,
                    "temporal_version": temporal_version,
                    "include_sentences": include_sentences,
                }
            }
        )

        url = base_url.format(
            self.topic_api_url, self.tenant, project_id, groundtruth_id, item_id
        )
        res = self._perform_request("get", url, headers=headers, data=data)
        return self._process_response(res)
