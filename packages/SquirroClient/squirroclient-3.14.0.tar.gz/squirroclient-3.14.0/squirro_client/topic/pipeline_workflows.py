from typing import Optional, Union

from ..util import _dumps


class PipelineWorkflowMixin:
    #
    # Pipeline Workflows
    #

    def get_pipeline_workflows(self, project_id, omit_steps=False, omit_sources=False):
        """Return all pipeline workflows for project with `project_id`.

        :param project_id: id of the project within tenant
        :param omit_steps: whether to omit steps in the response for better
                           performance.
        :param omit_sources: whether to omit in the response the data sources
                             which are configured to use each pipeline
                             workflow.
        :return: A list of pipeline workflow dictionaries.

        Example::

            >>> client.get_pipeline_workflows('project_id_1')
            [{'id': 'pipeline_workflow_id_1',
              'project_id': 'project_id_1',
              'name': 'Pipeline Workflow 1',
              'project_default': True,
              'steps': [
                 {"name": "Pipelet",
                  "type": "pipelet",
                  "display_name": "PermID OpenCalais",
                  "id": "XPOxEgNSR3W4TirOwOA-ng",
                  "config": {"config": {"api_key": "AGa865", "confidence": 0.7},
                             "pipelet": "searches/PermID Entities Enrichment"},
                 },
                 {"name": "Index",
                  "type": "index",
                  ...
                 }
              ]
             },
             {'id': 'pipeline_workflow_id_2',
              ...
             },
             ...
            ]
        """
        headers = {"Content-Type": "application/json"}

        url = (
            f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/"
            "pipeline_workflows"
        )

        data_dict = dict(omit_steps=omit_steps, omit_sources=omit_sources)

        res = self._perform_request("get", url, data=_dumps(data_dict), headers=headers)

        return self._process_response(res)

    def get_pipeline_workflow(
        self, project_id, workflow_id, omit_steps=False, omit_sources=False
    ):
        """Return a specific pipeline workflow `workflow_id` in project with `project_id`.

        :param project_id: project id
        :param workflow_id: pipeline workflow id
        :param omit_steps: whether to omit steps in the response for better
                           performance.
        :param omit_sources: whether to omit in the response the data sources which are
                             configured to use this pipeline workflow.
        :return: A dictionary of the pipeline workflow.

        Example::

            >>> client.get_pipeline_workflow('project_id_1', 'workflow_id_1')
            {'id': 'pipeline_workflow_id_1',
             'project_id': 'project_id_1',
             'name': 'Pipeline Workflow 1',
             'steps': [
                {"name": "Pipelet",
                 "type": "pipelet",
                 "display_name": "PermID OpenCalais",
                 "id": "XPOxEgNSR3W4TirOwOA-ng",
                 "config": {"config": {"api_key": "AGa8A65", "confidence": 0.7},
                            "pipelet": "searches/PermID Entities Enrichment"},
                },
                {"name": "Index",
                 "type": "index",
                  ...
                }
             ]
            }
        """
        headers = {"Content-Type": "application/json"}

        url = (
            f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/"
            f"pipeline_workflows/{workflow_id}"
        )

        data_dict = dict(omit_steps=omit_steps, omit_sources=omit_sources)

        res = self._perform_request("get", url, data=_dumps(data_dict), headers=headers)

        return self._process_response(res)

    def new_pipeline_workflow(self, project_id, name, steps=None):
        """Creates a new pipeline workflow.

        :param project_id: project id
        :param name: name of workflow
        :param steps: list of sets of properties that require at least the
            step `type` to be specified and be one of a list of known
            types. Steps need to be ordered in a specific way. If `steps` is
            None or the empty list, the default steps will be set.

        Example::

            >>> client.new_pipeline_workflow(
            >>>     project_id='project_id_1',
            >>>     name='Pipeline Workflow 1',
            >>>     steps=[{"name": "Index",
            >>>             "type": "index"}])
        """
        if name is None:
            raise ValueError("Name needs to be specified.")

        data_dict = dict(name=name)

        if steps is not None:
            if not isinstance(steps, list):
                raise ValueError("Steps need to be a list of dicts")
            if steps:
                data_dict["steps"] = steps

        headers = {"Content-Type": "application/json"}

        url = (
            f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/"
            "pipeline_workflows"
        )

        res = self._perform_request(
            "post", url, data=_dumps(data_dict), headers=headers
        )

        return self._process_response(res, [201])

    def modify_pipeline_workflow(
        self, project_id, workflow_id, name=None, steps=None, project_default=None
    ):
        """Updates a pipeline workflow

        :param project_id: project id
        :param workflow_id: pipeline workflow id
        :param name: name of workflow or None if no change
        :param steps: list of sets of properties that require at least the
            step `type` to be specified and be one of a list of known
            types. Steps need to be ordered in a specific way. Can be None if no
            change.
        :param project_default: whether pipeline workflow should become the new
            project default workflow. Allowed values are True or None. It is not
            possible to clear the project_default because at any time exactly
            one project default pipeline workflow needs to exist. To change the
            project default workflow, instead set True on the new default
            workflow which will as a side-effect clear the previous default.

        Example::

            >>> client.modify_pipeline_workflow(
            >>>     project_id='project_id_1',
            >>>     workflow_id='pipeline_workflow_id_1',
            >>>     name='Pipeline Workflow 1',
            >>>     steps=[{"name": "Index",
            >>>             "type": "index"}])
        """
        data_dict = {}

        if name is not None:
            data_dict["name"] = name

        if steps is not None:
            data_dict["steps"] = steps

        if project_default is not None:
            data_dict["project_default"] = project_default

        headers = {"Content-Type": "application/json"}

        url = (
            f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/"
            f"pipeline_workflows/{workflow_id}"
        )

        res = self._perform_request("put", url, data=_dumps(data_dict), headers=headers)

        return self._process_response(res, [200])

    def delete_pipeline_workflow(self, project_id, workflow_id):
        """Deletes a pipeline workflow as long as it is no longer needed.
        Project default workflows cannot be deleted and neither can workflows
        that still have sources referring to them.

        :param project_id: project id
        :param workflow_id: pipeline workflow id
        :return: 204 if deletion has been successful

        Example::

            >>> client.delete_pipeline_workflow(
            >>>     project_id='project_id_1',
            >>>     workflow_id='pipeline_workflow_id_1',
        """
        url = (
            f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/"
            f"pipeline_workflows/{workflow_id}"
        )

        res = self._perform_request("delete", url)

        return self._process_response(res, [204])

    def move_pipeline_workflow_step(self, project_id, workflow_id, step_id, after):
        """Move a pipelet step within a workflow.

        :param project_id: id of project that owns the workflow
        :param workflow_id: pipeline workflow id
        :param step_id: id of the pipelet step to move
        :param after: id of the step after which the pipelet step
                      should be moved or None if pipelet is supposed to be first
        :return: updated workflow

        Example::

            >>> client.move_pipeline_workflow_step('2aEVClLRRA-vCCIvnuEAvQ',
            ...                                    'Ue1OceLkQlyz21wpPqml9Q',
            ...                                    'nJXpKUSERmSgQRjxX7LrZw',
            ...                                    'language-detection')
        """
        headers = {"Content-Type": "application/json"}

        url = (
            f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/"
            f"pipeline_workflows/{workflow_id}/steps/{step_id}/move"
        )

        res = self._perform_request(
            "put", url, data=_dumps({"after": after}), headers=headers
        )

        return self._process_response(res, [202])

    def get_pipeline_workflows_presets(self, project_id):
        """Return a list of pre-made pipeline workflows for covering various use cases.

        :param project_id: the Id of the project
        :return: a list of dictionaries where each dictionary represents a pipeline
                 workflow preset.
        """
        headers = {"Accept": "application/json"}

        url = f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/pipeline_workflows/presets"

        res = self._perform_request("get", url, headers=headers)

        return self._process_response(res)

    def rerun_pipeline_workflow(
        self,
        project_id: str,
        workflow_id: str,
        from_index: bool = False,
        step_ids: Optional[Union[str, list[str]]] = None,
        run_linked_steps: Optional[bool] = None,
        query: Optional[str] = None,
        include_sub_items: Optional[bool] = None,
        include_entities: Optional[bool] = None,
        priority: Optional[str] = None,
    ):
        """Rerun a pipeline workflow using the data of its configured data sources.

        :param project_id: the Id of the project that this workflow belongs to.
        :param workflow_id: the Id of the pipeline workflow to rerun.
        :param from_index: if True then this flag indicates that rerun will use the
            indexed Squirro items as input to the workflow for ingestion.
        :param step_ids: the IDs of one or more steps of the provided pipeline workflow
            that the rerun from index will be executed on. The rest of the steps in the
            workflow will be omitted.
        :param run_linked_steps: a flag which indicates whether to rerun from index the
            linked steps of the step provided by the `step_ids`. It has an effect only
            when the `step_ids` parameter is provided. If multiple step IDs are included
            in the provided `step_ids`, then only the first step in the list, along with
            its set of linked steps, will rerun from index.
        :param query: a query expressed in Squirro's Query Syntax [1]. It has an effect
            only with the rerun from index, in order to rerun only the items returned by
            the query.
            [1] https://go.squirro.com/query-syntax
        :param include_sub_items: if set to True, then the sub-items of the items will
            also be fetched and included in the rerun data. If set to False, then no
            sub-items will be fetched. If set to None (default), then the behaviour will
            be determined by the value of the project setting:
            ``datasource.rerun.index.include-sub-items``.
            This option has an effect only with the rerun from index mode.
        :param include_entities: if set to True, then the entities of the items will also
            be fetched and included in the rerun data. If set to False, then no entities
            will be fetched. If set to None (default), then the behaviour will be
            determined by the value of the project setting:
            ``datasource.rerun.index.include-entities``.
            This option has an effect only with the rerun from index mode.
        :param priority: the priority assigned to the rerun batches. It can be one of
            the following values: "low", "normal", "high". If not provided, the default
            priority ("normal") will be used.
            This option has an effect only with the rerun from index mode.

        Example::

            >>> client.rerun_pipeline_workflow(
            ...    "EcKKf_dxRe-xrCB8g1fGCg",
            ...    "Or0UiK-qROeE1x8kVlBZkQ",
            ...    from_index=True,
            ...    step_ids=["aiNJX35dRhCfqc3a3l84PA", "qsXDOkMvQ-62-iM7O1Fp5w"],
            ...    query="source:g2hqOvX8SZmR7R2RPmMlDw"
            ...    priority="high")

        The above example will invoke rerun from index for the workflow with id
        `Or0UiK-qROeE1x8kVlBZkQ` of the project with id `EcKKf_dxRe-xrCB8g1fGCg`, using
        only the 2 provided steps identified by their ids (steps are already part of the
        workflow), and only on the items of the source with id `g2hqOvX8SZmR7R2RPmMlDw`
        (the workflow can be configured to be used by many sources, but we want to rerun
        only on the items of a specific configured source). The rerun item batches will
        be created with high priority.
        """
        headers = {"Content-Type": "application/json"}

        params = {"from_index": from_index}

        data = {}
        if step_ids:
            data["step_ids"] = step_ids if isinstance(step_ids, list) else [step_ids]
        if run_linked_steps:
            data["run_linked_steps"] = run_linked_steps
        if query:
            data["query"] = query
        if include_sub_items is not None:
            data["include_sub_items"] = include_sub_items
        if include_entities is not None:
            data["include_entities"] = include_entities
        if priority:
            data["priority"] = priority

        url = (
            f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/"
            f"pipeline_workflows/{workflow_id}/rerun"
        )

        res = self._perform_request(
            "post", url, params=params, data=_dumps(data), headers=headers
        )

        return self._process_response(res)

    def add_model_to_pipeline_workflow(
        self, project_id, workflow_id, model_id, document_label=None
    ):
        """Updates a pipeline workflow with a published model from AI Studio.

        :param project_id: project id
        :param workflow_id: pipeline workflow id
        :param model_id: id of published model in AI Studio
        :param document_label: (required only for document-level classifiers) **name** (not display name) of the label that the model should use to classify documents (the label must exist).

        Example::

            >>> client.add_model_to_pipeline_workflow(
            >>>     project_id='project_id_1',
            >>>     workflow_id='pipeline_workflow_id_1',
            >>>     model_id="model_id_1",
            >>>     document_label="ml_classification")
        """
        headers = {"Content-Type": "application/json"}
        url = f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/pipeline_sections"

        res = self._perform_request("get", url, headers=headers)

        data = {"pipeline_sections": res.json()}

        if document_label is not None:
            data["document_label"] = document_label

        url = (
            f"{self.topic_api_url}/v0/{self.tenant}/projects/{project_id}/"
            f"pipeline_workflows/{workflow_id}/model/{model_id}"
        )

        res = self._perform_request("put", url, data=_dumps(data), headers=headers)

        return self._process_response(res, [204])
