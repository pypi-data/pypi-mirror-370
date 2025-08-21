# SPDX-FileCopyrightText: 2022-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


from typing import AsyncIterator, Iterable, Union

from pontos.github.api.client import GitHubAsyncREST
from pontos.github.api.helper import JSON


class GitHubAsyncRESTLabels(GitHubAsyncREST):
    async def get_all(
        self,
        repo: str,
        issue: Union[int, str],
    ) -> AsyncIterator[str]:
        """
        Get all labels that are set in the issue/pr

        Args:
            repo:   GitHub repository (owner/name) to use
            issue:  Issue/Pull request number

        Returns:
            An async iterator yielding the labels

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    async for label in api.labels.get_all("foo/bar", 123):
                        print(label)
        """
        api = f"/repos/{repo}/issues/{issue}/labels"
        params = {"per_page": "100"}

        async for response in self._client.get_all(api, params=params):
            response.raise_for_status()
            data: JSON = response.json()

            for label in data:
                yield label["name"]  # type: ignore

    async def delete_all(self, repo: str, issue: Union[int, str]) -> None:
        """
        Deletes all labels in the issue/pr.

        Args:
            repo:   GitHub repository (owner/name) to use
            issue:  Issue/Pull request number

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    await api.labels.delete_all("foo/bar", 123)
        """
        api = f"/repos/{repo}/issues/{issue}/labels"
        response = await self._client.delete(api)
        response.raise_for_status()

    async def set_all(
        self, repo: str, issue: Union[int, str], labels: Iterable[str]
    ) -> None:
        """
        Set labels in the issue/pr.

        Args:
            repo:   GitHub repository (owner/name) to use
            issue:  Issue/Pull request number
            labels: Iterable of labels, that should be set. Existing labels will
                be overwritten.

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    await api.labels.set_all("foo/bar", 123, ["bug", "doc"])
        """
        api = f"/repos/{repo}/issues/{issue}/labels"
        data: JSON = {"labels": labels}  # type: ignore
        response = await self._client.post(api, data=data)
        response.raise_for_status()
