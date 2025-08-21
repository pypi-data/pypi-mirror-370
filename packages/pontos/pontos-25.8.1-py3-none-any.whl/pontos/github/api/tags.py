# SPDX-FileCopyrightText: 2022-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from datetime import datetime
from typing import Any, AsyncIterator, Dict, Optional, Union

from pontos.github.api.client import GitHubAsyncREST
from pontos.github.models.tag import GitObjectType, RepositoryTag, Tag
from pontos.helper import enum_or_value


class GitHubAsyncRESTTags(GitHubAsyncREST):
    async def create(
        self,
        repo: str,
        tag: str,
        message: str,
        name: str,
        email: str,
        git_object: str,
        *,
        git_object_type: Optional[
            Union[GitObjectType, str]
        ] = GitObjectType.COMMIT,
        date: Optional[datetime] = None,
    ) -> Tag:
        """
        Create a new Git tag

        https://docs.github.com/en/rest/git/tags#create-a-tag-object

        Args:
            repo: GitHub repository (owner/name) to use
            tag: The tag's name. This is typically a version (e.g., "v0.0.1").
            message: The tag message.
            name: The name of the author of the tag
            email: The email of the author of the tag
            git_object: The SHA of the git object this is tagging.
            git_object_type: The type of the object we're tagging. Normally this
                is a commit type but it can also be a tree or a blob.
            date: When this object was tagged.

        Raises:
            HTTPStatusError: If the request was invalid

        Returns:
            A new git tag

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    tag = await api.tags.create(
                        "foo/bar",
                        "v1.2.3",
                        "Create tag v1.2.3",
                        "John Doe",
                        "john@doe.com",
                        e746420,
                    )
                    print(tag)
        """
        data = {
            "tag": tag,
            "message": message,
            "object": git_object,
            "type": enum_or_value(git_object_type),
            "tagger": {
                "name": name,
                "email": email,
            },
        }

        if date:
            data["tagger"]["date"] = date.isoformat(timespec="seconds")

        api = f"/repos/{repo}/git/tags"
        response = await self._client.post(api, data=data)
        response.raise_for_status()
        return Tag.from_dict(response.json())

    async def create_tag_reference(
        self,
        repo: str,
        tag: str,
        sha: str,
    ) -> None:
        """
        Create git tag reference (A real tag in git).

        https://docs.github.com/en/rest/git/refs#create-a-reference

        Args:
            repo: The name of the repository.
                The name is not case sensitive.
            tag: Github tag name.
            sha: The SHA1 value for this Github tag.

        Raises:
            HTTPStatusError: If the request was invalid

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    await api.tags.create_tag_reference(
                        "foo/bar",
                        "v1.2.3",
                        e746420,
                    )
        """

        data: Dict[str, Any] = {
            "ref": f"refs/tags/{tag}",
            "sha": sha,
        }

        api = f"/repos/{repo}/git/refs"
        response = await self._client.post(api, data=data)
        response.raise_for_status()

    async def get(self, repo: str, tag_sha: str) -> Tag:
        """
        Get information about a git tag

        Args:
            repo: GitHub repository (owner/name) to use
            tag_sha: SHA of the git tag object

        Raises:
            HTTPStatusError: If the request was invalid

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    tag = await api.tags.get("foo/bar", "e746420")
                    print(tag)
        """
        api = f"/repos/{repo}/git/tags/{tag_sha}"
        response = await self._client.get(api)
        response.raise_for_status()
        return Tag.from_dict(response.json())

    async def get_all(self, repo: str) -> AsyncIterator[RepositoryTag]:
        """
        Get information about all git tags

        Args:
            repo: GitHub repository (owner/name) to use

        Raises:
            HTTPStatusError: If the request was invalid

        Example:
            .. code-block:: python

                from pontos.github.api import GitHubAsyncRESTApi

                async with GitHubAsyncRESTApi(token) as api:
                    async for tag in api.tags.get_all(
                        "foo/bar"
                    ):
                        print(tag)
        """
        api = f"/repos/{repo}/git/tags"
        params = {"per_page": "100"}

        async for response in self._client.get_all(api, params=params):
            response.raise_for_status()
            for tag in response.json():
                yield RepositoryTag.from_dict(tag)
