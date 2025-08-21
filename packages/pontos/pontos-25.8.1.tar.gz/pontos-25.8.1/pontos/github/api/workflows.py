# SPDX-FileCopyrightText: 2022-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from typing import Any, AsyncIterator, Dict, Optional, Union

from pontos.github.api.client import GitHubAsyncREST
from pontos.github.models.base import Event
from pontos.github.models.workflow import (
    Workflow,
    WorkflowRun,
    WorkflowRunStatus,
)
from pontos.helper import enum_or_value


class GitHubAsyncRESTWorkflows(GitHubAsyncREST):
    def get_all(self, repo: str) -> AsyncIterator[Workflow]:
        """
        List all workflows of a repository

        https://docs.github.com/en/rest/actions/workflows#list-repository-workflows

        Args:
            repo: GitHub repository (owner/name) to use

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            An async iterator yielding workflows

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    async for workflow in api.workflows.get_all("foo/bar"):
                        print(workflow)
        """
        api = f"/repos/{repo}/actions/workflows"
        return self._get_paged_items(api, "workflows", Workflow)  # type: ignore

    async def get(self, repo: str, workflow: Union[str, int]) -> Workflow:
        """
        Get the information for the given workflow

        https://docs.github.com/en/rest/actions/workflows#get-a-workflow

        Args:
            repo: GitHub repository (owner/name) to use
            workflow: ID of the workflow or workflow file name. For example
                `main.yml`.

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            Information about the workflow

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    workflow = await api.workflows.get("foo/bar", "ci.yml")
                    print(workflow)
        """
        api = f"/repos/{repo}/actions/workflows/{workflow}"
        response = await self._client.get(api)
        response.raise_for_status()
        return Workflow.from_dict(response.json())

    async def create_workflow_dispatch(
        self,
        repo: str,
        workflow: Union[str, int],
        *,
        ref: str,
        inputs: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Create a workflow dispatch event to manually trigger a GitHub Actions
        workflow run.

        https://docs.github.com/en/rest/actions/workflows#create-a-workflow-dispatch-event

        Args:
            repo: GitHub repository (owner/name) to use
            workflow: ID of the workflow or workflow file name. For example
                `main.yml`.
            ref: The git reference for the workflow. The reference can be a
                branch or tag name.
            inputs: Input keys and values configured in the workflow file. Any
                default properties configured in the workflow file will be used
                when inputs are omitted.

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                with GitHubAsyncRESTApi(token) as api:
                    await api.workflows.create_workflow_dispatch(
                        "foo/bar", "ci.yml", ref="main"
                    )
        """
        api = f"/repos/{repo}/actions/workflows/{workflow}/dispatches"
        data: Dict[str, Any] = {"ref": ref}

        if inputs:
            data["inputs"] = inputs

        response = await self._client.post(api, data=data)
        response.raise_for_status()

    def get_workflow_runs(
        self,
        repo: str,
        workflow: Optional[Union[str, int]] = None,
        *,
        actor: Optional[str] = None,
        branch: Optional[str] = None,
        event: Optional[Union[Event, str]] = None,
        status: Optional[Union[WorkflowRunStatus, str]] = None,
        created: Optional[str] = None,
        exclude_pull_requests: Optional[bool] = None,
    ) -> AsyncIterator[WorkflowRun]:
        # pylint: disable=line-too-long
        """
        List all workflow runs of a repository or of a specific workflow.

        https://docs.github.com/en/rest/actions/workflow-runs#list-workflow-runs-for-a-repository
        https://docs.github.com/en/rest/actions/workflow-runs#list-workflow-runs-for-a-workflow

        Args:
            repo: GitHub repository (owner/name) to use
            workflow: Optional ID of the workflow or workflow file name. For
                example `main.yml`.
            actor: Only return workflow runs of this user ID.
            branch: Only return workflow runs for a specific branch.
            event: Only return workflow runs triggered by the event specified.
                For example, `push`, `pull_request` or `issue`.
                For more information, see https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows.
            status: Only return workflow runs with the check run status or
                conclusion that specified. For example, a conclusion can be
                `success` or a status can be `in_progress`. Can be one of:
                `completed`, `action_required`, `cancelled`, `failure`,
                `neutral`, `skipped`, `stale`, `success`, `timed_out`,
                `in_progress`, `queued`, `requested`, `waiting`.
            created: Only returns workflow runs created within the given
                date-time range. For more information on the syntax, see
                https://docs.github.com/en/search-github/getting-started-with-searching-on-github/understanding-the-search-syntax#query-for-dates
            exclude_pull_requests: If true pull requests are omitted from the
                response.

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            An async iterator yielding workflow runs

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    async for run in api.workflows.get_workflow_runs(
                        "foo/bar",
                        "ci.yml"
                    ):
                        print(run)
        """

        api = (
            f"/repos/{repo}/actions/workflows/{workflow}/runs"
            if workflow
            else f"/repos/{repo}/actions/runs"
        )
        params: Dict[str, Any] = {}
        if actor:
            params["actor"] = actor
        if branch:
            params["branch"] = branch
        if event:
            params["event"] = enum_or_value(event)
        if status:
            params["status"] = enum_or_value(status)
        if created:
            params["created"] = created
        if exclude_pull_requests is not None:
            params["exclude_pull_requests"] = exclude_pull_requests

        return self._get_paged_items(  # type: ignore
            api, "workflow_runs", WorkflowRun, params=params
        )

    async def get_workflow_run(
        self, repo: str, run: Union[str, int]
    ) -> WorkflowRun:
        """
        Get information about a single workflow run

        https://docs.github.com/en/rest/actions/workflow-runs#get-a-workflow-run

        Args:
            repo: GitHub repository (owner/name) to use
            run: The ID of the workflow run

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            Information about the workflow run

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    run = await api.workflows.get_workflow_run("foo/bar", 123)
                    print(run)
        """
        api = f"/repos/{repo}/actions/runs/{run}"
        response = await self._client.get(api)
        response.raise_for_status()
        return WorkflowRun.from_dict(response.json())
