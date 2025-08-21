# Copyright (C) 2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


from abc import ABC

from pontos.models import StrEnum

from .base import SortOrder

__all__ = (
    "InDescriptionQualifier",
    "InNameQualifier",
    "InReadmeQualifier",
    "InTopicsQualifier",
    "IsPrivateQualifier",
    "IsPublicQualifier",
    "NotQualifier",
    "OrganizationQualifier",
    "Qualifier",
    "RepositoryQualifier",
    "RepositorySort",
    "SortOrder",
    "UserQualifier",
)


class RepositorySort(StrEnum):
    """
    Sort repositories by

    Attributes:
        STARS: GitHub starts
        FORKS: GitHub forks
        HELP_WANTED_ISSUES: Number of issues with help wanted label
        UPDATED: Last updated
    """

    STARS = "stars"
    FORKS = "forks"
    HELP_WANTED_ISSUES = "help-wanted-issues"
    UPDATED = "updated"


class Qualifier(ABC):
    """
    An abstract base class for search qualifiers

    Attributes:
        operator: The search operator
        term: The search term
    """

    operator: str
    term: str

    def __str__(self) -> str:
        """ """
        return f"{self.operator}:{self.term}"


class NotQualifier(Qualifier):
    """
    Qualifier for negating another qualifier

    Example:

        Exclude a repository from a search

        .. code-block:: python

            from pontos.github.models import NotQualifier, RepositoryQualifier

            qualifier = NotQualifier(RepositoryQualifier("foo/bar"))
    """

    def __init__(self, qualifier: Qualifier) -> None:
        self.qualifier = qualifier

    def __str__(self) -> str:
        return f"-{str(self.qualifier)}"


class InQualifier(Qualifier):
    operator = "in"


class InNameQualifier(InQualifier):
    """
    Qualifier for searching in repository names
    """

    term = "name"


class InDescriptionQualifier(InQualifier):
    """
    Qualifier for searching in repository descriptions
    """

    term = "description"


class InTopicsQualifier(InQualifier):
    """
    Qualifier for searching in repository topics
    """

    term = "topics"


class InReadmeQualifier(InQualifier):
    """
    Qualifier for searching in repository READMEs
    """

    term = "readme"


class RepositoryQualifier(Qualifier):
    """
    Qualifier for searching within a specific repository
    """

    operator = "repo"

    def __init__(self, repository: str) -> None:
        """
        Search within a repository

        Args:
            repository: owner/repo
        """
        self.term = repository


class OrganizationQualifier(Qualifier):
    """
    Qualifier for searching within a specific organization
    """

    operator = "org"

    def __init__(self, organization: str) -> None:
        """
        Search within an organization

        Args:
            organization: Name of the organization to search within
        """
        self.term = organization


class UserQualifier(Qualifier):
    """
    Qualifier for searching within a specific user space
    """

    operator = "user"

    def __init__(self, user: str) -> None:
        """
        Search within an user space

        Args:
            user: Name of the user
        """
        self.term = user


class IsPublicQualifier(Qualifier):
    """
    Qualifier for searching for public repositories
    """

    operator = "is"
    term = "public"


class IsPrivateQualifier(Qualifier):
    """
    Qualifier for searching for private repositories
    """

    operator = "is"
    term = "private"
