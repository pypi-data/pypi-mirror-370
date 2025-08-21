# SPDX-FileCopyrightText: 2022-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from typing import Any, Iterable, Optional, Union

from pontos.github.api.client import GitHubAsyncREST
from pontos.github.api.helper import JSON_OBJECT
from pontos.github.models.organization import (
    GitIgnoreTemplate,
    LicenseType,
    MergeCommitMessage,
    MergeCommitTitle,
    Repository,
    SquashMergeCommitMessage,
    SquashMergeCommitTitle,
)
from pontos.helper import enum_or_value
from pontos.typing import SupportsStr


class GitHubAsyncRESTRepositories(GitHubAsyncREST):
    async def get(self, repo: str) -> Repository:
        """
        Get a repository

        https://docs.github.com/en/rest/repos/repos#get-a-repository

        Args:
            repo: GitHub repository (owner/name) to request

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            Information about the repository

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    repo = await api.repositories.get("foo/bar")
                    print(repo)
        """
        api = f"/repos/{repo}"
        response = await self._client.get(api)
        response.raise_for_status()
        return Repository.from_dict(response.json())

    async def delete(self, repo: str) -> None:
        """
        Delete a repository

        Args:
            repo: GitHub repository (owner/name) to delete

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    await api.repositories.delete("foo/bar")
        """
        api = f"/repos/{repo}"
        response = await self._client.delete(api)
        response.raise_for_status()

    async def create(
        self,
        organization: str,
        name: str,
        *,
        description: Optional[str] = None,
        homepage: Optional[str] = None,
        private: Optional[bool] = False,
        has_issues: Optional[bool] = True,
        has_projects: Optional[bool] = True,
        has_wiki: Optional[bool] = True,
        has_downloads: Optional[bool] = True,
        is_template: Optional[bool] = False,
        team_id: Optional[SupportsStr] = None,
        auto_init: Optional[bool] = False,
        gitignore_template: Optional[Union[GitIgnoreTemplate, str]] = None,
        license_template: Optional[Union[LicenseType, str]] = None,
        allow_squash_merge: Optional[bool] = True,
        allow_merge_commit: Optional[bool] = True,
        allow_rebase_merge: Optional[bool] = True,
        allow_auto_merge: Optional[bool] = False,
        allow_update_branch: Optional[bool] = False,
        delete_branch_on_merge: Optional[bool] = False,
        squash_merge_commit_title: Optional[
            Union[SquashMergeCommitTitle, str]
        ] = None,
        squash_merge_commit_message: Optional[
            Union[SquashMergeCommitMessage, str]
        ] = None,
        merge_commit_title: Optional[Union[MergeCommitTitle, str]] = None,
        merge_commit_message: Optional[Union[MergeCommitMessage, str]] = None,
    ) -> Repository:
        """
        Create a new repository at GitHub

        https://docs.github.com/en/rest/repos/repos#create-an-organization-repository

        Args:
            organization: Name of the GitHub organization where to create the
                new repository.
            name: Name of the GitHub repository.
            description: Description of the GitHub repository.
            homepage: A URL with more information about the repository.
            private: Whether the repository is private. Default: False.
            has_issues: Either True to enable issues for this repository or
                False to disable them. Default: True
            has_projects: Either True to enable projects for this repository or
                False to disable them. Note: If you're creating a repository in
                an organization that has disabled repository projects, the
                default is false, and if you pass true, the API returns an
                error. Default: true.
            has_wiki: Either True to enable the wiki for this repository or
                False to disable it. Default: True.
            has_downloads: Whether downloads are enabled. Default: True.
            is_template: Either True to make this repo available as a template
                repository or False to prevent it. Default: False.
            team_id: The id of the team that will be granted access to this
                repository. This is only valid when creating a repository in an
                organization.
            auto_init: Pass True to create an initial commit with empty README.
                Default: False.
            gitignore_template: Desired language or platform .gitignore template
                to apply. Use the name of the template without the extension.
                For example, "Haskell".
            license_template: Choose an open source license template that best
                suits your needs, and then use the license keyword as the
                license_template string. For example, "mit" or "mpl-2.0".
            allow_squash_merge: Either true to allow squash-merging pull
                requests, or false to prevent squash-merging. Default: True
            allow_merge_commit: Either True to allow merging pull requests with
                a merge commit, or False to prevent merging pull requests with
                merge commits. Default: True.
            allow_rebase_merge: Either True to allow rebase-merging pull
                requests, or False to prevent rebase-merging. Default: True.
            allow_auto_merge: Either True to allow auto-merge on pull requests,
                or False to disallow auto-merge. Default: False.
            allow_update_branch: Either True to always allow a pull request head
                branch, that is behind its base branch, to be updated, even if
                it is not required to be up to date before merging, or False
                otherwise. Default: False.
            delete_branch_on_merge: Either True to allow automatically deleting
                head branches when pull requests are merged, or False to prevent
                automatic deletion. Default: False.
            squash_merge_commit_title: The default value for a squash merge
                commit title:

                * "PR_TITLE" - default to the pull request's title.
                * "COMMIT_OR_PR_TITLE" - default to the commit's title (if
                    only one commit) or the pull request's title (when more
                    than one commit).

                Can be one of: "PR_TITLE", "COMMIT_OR_PR_TITLE"
            squash_merge_commit_message: The default value for a squash merge
                commit message:

                * "PR_BODY" - default to the pull request's body.
                * "COMMIT_MESSAGES" - default to the branch's commit messages.
                * "BLANK" - default to a blank commit message.

                Can be one of: "PR_BODY", "COMMIT_MESSAGES", "BLANK"
            merge_commit_title: The default value for a merge commit title.

                * "PR_TITLE" - default to the pull request's title.
                * "MERGE_MESSAGE" - default to the classic title for a merge
                    message (e.g., Merge pull request #123 from branch-name).

                Can be one of: "PR_TITLE", "MERGE_MESSAGE"
            merge_commit_message: The default value for a merge commit message.

                * "PR_TITLE" - default to the pull request's title.
                * "PR_BODY" - default to the pull request's body.
                * "BLANK" - default to a blank commit message.

                Can be one of: "PR_BODY", "PR_TITLE", "BLANK"

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    repo = await api.repositories.create(
                        "foo/bar",
                        "baz",
                        description="A new baz repository",
                        private=True,
                        allow_squash_merge=True,
                        allow_merge_commit=False,
                        allow_rebase_merge=True,
                        allow_auto_merge=True,
                        allow_update_branch=True,
                        delete_branch_on_merge=True,
                    )
        """
        api = f"/orgs/{organization}/repos"
        data: JSON_OBJECT = {"name": name}

        if description:
            data["description"] = description
        if homepage:
            data["homepage"] = homepage
        if private is not None:
            data["private"] = private
        if has_issues is not None:
            data["has_issues"] = has_issues
        if has_projects is not None:
            data["has_projects"] = has_projects
        if has_wiki is not None:
            data["has_wiki"] = has_wiki
        if is_template is not None:
            data["is_template"] = is_template
        if team_id:
            data["team_id"] = str(team_id)
        if has_downloads is not None:
            data["has_downloads"] = has_downloads
        if auto_init is not None:
            data["auto_init"] = auto_init
        if gitignore_template:
            data["gitignore_template"] = (
                gitignore_template.value
                if isinstance(gitignore_template, GitIgnoreTemplate)
                else gitignore_template
            )
        if license_template:
            data["license_template"] = enum_or_value(license_template)
        if allow_squash_merge is not None:
            data["allow_squash_merge"] = allow_squash_merge
        if allow_merge_commit is not None:
            data["allow_merge_commit"] = allow_merge_commit
        if allow_rebase_merge is not None:
            data["allow_rebase_merge"] = allow_rebase_merge
        if allow_auto_merge is not None:
            data["allow_auto_merge"] = allow_auto_merge
        if allow_update_branch is not None:
            data["allow_update_branch"] = allow_update_branch
        if delete_branch_on_merge is not None:
            data["delete_branch_on_merge"] = delete_branch_on_merge
        if squash_merge_commit_title:
            data["squash_merge_commit_title"] = enum_or_value(
                squash_merge_commit_title
            )
        if squash_merge_commit_message:
            data["squash_merge_commit_message"] = enum_or_value(
                squash_merge_commit_message
            )
        if merge_commit_title:
            data["merge_commit_title"] = enum_or_value(merge_commit_title)
        if merge_commit_message:
            data["merge_commit_message"] = enum_or_value(merge_commit_message)

        response = await self._client.post(api, data=data)
        response.raise_for_status()
        return Repository.from_dict(response.json())

    async def archive(self, repo: str) -> None:
        """
        Archive a GitHub repository

        WARNING: It is not possible to unarchive a repository via the API.

        Args:
            repo: GitHub repository (owner/name) to update

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    await api.repositories.archive("foo/bar")
        """
        api = f"/repos/{repo}"

        data: JSON_OBJECT = {"archived": True}
        response = await self._client.post(api, data=data)
        response.raise_for_status()

    async def update(
        self,
        repo: str,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        homepage: Optional[str] = None,
        private: Optional[bool] = False,
        has_issues: Optional[bool] = True,
        has_projects: Optional[bool] = True,
        has_wiki: Optional[bool] = True,
        is_template: Optional[bool] = False,
        default_branch: Optional[str] = None,
        allow_squash_merge: Optional[bool] = True,
        allow_merge_commit: Optional[bool] = True,
        allow_rebase_merge: Optional[bool] = True,
        allow_auto_merge: Optional[bool] = False,
        allow_update_branch: Optional[bool] = False,
        delete_branch_on_merge: Optional[bool] = False,
        squash_merge_commit_title: Optional[
            Union[SquashMergeCommitTitle, str]
        ] = None,
        squash_merge_commit_message: Optional[
            Union[SquashMergeCommitMessage, str]
        ] = None,
        merge_commit_title: Optional[Union[MergeCommitTitle, str]] = None,
        merge_commit_message: Optional[Union[MergeCommitMessage, str]] = None,
        allow_forking: Optional[bool] = False,
        web_commit_signoff_required: Optional[bool] = False,
    ) -> Repository:
        """
        Create a new repository at GitHub

        https://docs.github.com/en/rest/repos/repos#update-a-repository

        Args:
            repo: GitHub repository (owner/name) to update
            name: New name of the GitHub repository.
            description: Description of the GitHub repository.
            homepage: A URL with more information about the repository.
            private: Whether the repository is private. Default: False.
            has_issues: Either True to enable issues for this repository or
                False to disable them. Default: True
            has_projects: Either True to enable projects for this repository or
                False to disable them. Note: If you're creating a repository in
                an organization that has disabled repository projects, the
                default is false, and if you pass true, the API returns an
                error. Default: true.
            has_wiki: Either True to enable the wiki for this repository or
                False to disable it. Default: True.
            is_template: Either True to make this repo available as a template
                repository or False to prevent it. Default: False.
            default_branch: Updates the default branch for this repository.
            allow_squash_merge: Either true to allow squash-merging pull
                requests, or false to prevent squash-merging. Default: True
            allow_merge_commit: Either True to allow merging pull requests with
                a merge commit, or False to prevent merging pull requests with
                merge commits. Default: True.
            allow_rebase_merge: Either True to allow rebase-merging pull
                requests, or False to prevent rebase-merging. Default: True.
            allow_auto_merge: Either True to allow auto-merge on pull requests,
                or False to disallow auto-merge. Default: False.
            allow_update_branch: Either True to always allow a pull request head
                branch that is behind its base branch to be updated even if it
                is not required to be up to date before merging, or False
                otherwise. Default: False.
            delete_branch_on_merge: Either True to allow automatically deleting
                head branches when pull requests are merged, or False to prevent
                automatic deletion. Default: False.
            squash_merge_commit_title: The default value for a squash merge
                commit title:

                * "PR_TITLE" - default to the pull request's title.
                * "COMMIT_OR_PR_TITLE" - default to the commit's title (if
                    only one commit) or the pull request's title (when more
                    than one commit).

                Can be one of: "PR_TITLE", "COMMIT_OR_PR_TITLE"
            squash_merge_commit_message: The default value for a squash merge
                commit message:

                * "PR_BODY" - default to the pull request's body.
                * "COMMIT_MESSAGES" - default to the branch's commit messages.
                * "BLANK" - default to a blank commit message.

                Can be one of: "PR_BODY", "COMMIT_MESSAGES", "BLANK"
            merge_commit_title: The default value for a merge commit title.

                * "PR_TITLE" - default to the pull request's title.
                * "MERGE_MESSAGE" - default to the classic title for a merge
                    message (e.g., Merge pull request #123 from branch-name).

                Can be one of: "PR_TITLE", "MERGE_MESSAGE"
            merge_commit_message: The default value for a merge commit message.

                * "PR_TITLE" - default to the pull request's title.
                * "PR_BODY" - default to the pull request's body.
                * "BLANK" - default to a blank commit message.

                Can be one of: "PR_BODY", "PR_TITLE", "BLANK"
            allow_forking: Either True to allow private forks, or False to
                prevent private forks. Default: False.
            web_commit_signoff_required: Either True to require contributors to
                sign off on web-based commits, or False to not require
                contributors to sign off on web-based commits. Default: False.

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            The updated repository

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    repo = await api.repositories.update(
                        "foo/bar",
                        allow_squash_merge=True,
                        allow_merge_commit=False,
                        allow_rebase_merge=True,
                        allow_auto_merge=True,
                        allow_update_branch=True,
                        delete_branch_on_merge=True,
                    )
        """
        api = f"/repos/{repo}"

        data: JSON_OBJECT = {}
        if name:
            data["name"] = name
        if description:
            data["description"] = description
        if homepage:
            data["homepage"] = homepage
        if private is not None:
            data["private"] = private
        if has_issues is not None:
            data["has_issues"] = has_issues
        if has_projects is not None:
            data["has_projects"] = has_projects
        if has_wiki is not None:
            data["has_wiki"] = has_wiki
        if is_template is not None:
            data["is_template"] = is_template
        if default_branch:
            data["default_branch"] = default_branch
        if allow_squash_merge is not None:
            data["allow_squash_merge"] = allow_squash_merge
        if allow_merge_commit is not None:
            data["allow_merge_commit"] = allow_merge_commit
        if allow_rebase_merge is not None:
            data["allow_rebase_merge"] = allow_rebase_merge
        if allow_auto_merge is not None:
            data["allow_auto_merge"] = allow_auto_merge
        if allow_update_branch is not None:
            data["allow_update_branch"] = allow_update_branch
        if delete_branch_on_merge is not None:
            data["delete_branch_on_merge"] = delete_branch_on_merge
        if squash_merge_commit_title:
            data["squash_merge_commit_title"] = enum_or_value(
                squash_merge_commit_title
            )
        if squash_merge_commit_message:
            data["squash_merge_commit_message"] = enum_or_value(
                squash_merge_commit_message
            )
        if merge_commit_title:
            data["merge_commit_title"] = enum_or_value(merge_commit_title)
        if merge_commit_message:
            data["merge_commit_message"] = enum_or_value(merge_commit_message)
        if allow_forking is not None:
            data["allow_forking"] = allow_forking
        if web_commit_signoff_required is not None:
            data["web_commit_signoff_required"] = web_commit_signoff_required

        response = await self._client.post(api, data=data)
        response.raise_for_status()
        return Repository.from_dict(response.json())

    async def topics(self, repo: str) -> Iterable[str]:
        """
        List all topics of a repository

        Args:
            repo: GitHub repository (owner/name) to list the topics for

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            An iterable of topics as string

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    topics = await api.repositories.topics("foo/bar")
        """
        api = f"/repos/{repo}/topics"
        response = await self._client.get(api)
        response.raise_for_status()

        data: dict[str, Any] = response.json()
        return data.get("names", [])

    async def update_topics(
        self, repo: str, new_topics: Iterable[str]
    ) -> Iterable[str]:
        """
        Replace all topics of a repository

        Args:
            repo: GitHub repository (owner/name) to update the topics for
            new_topics: Iterable of new topics to set on the repository

        Raises:
            HTTPStatusError: A httpx.HTTPStatusError is raised if the request
                failed.

        Returns:
            An iterable of topics as string

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    topics = await api.repositories.update_topics(
                        "foo/bar", ["foo", "bar"]
                    )
        """
        api = f"/repos/{repo}/topics"
        data = {"names": list(new_topics)}
        response = await self._client.put(api, data=data)  # type: ignore[arg-type] # noqa: E501
        response.raise_for_status()

        data: dict[str, Any] = response.json()
        return data.get("names", [])
