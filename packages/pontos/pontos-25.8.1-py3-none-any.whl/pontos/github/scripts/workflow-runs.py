# SPDX-FileCopyrightText: 2022-2023 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from argparse import ArgumentParser, Namespace

from rich.console import Console
from rich.table import Table

from pontos.github.api import GitHubAsyncRESTApi


def add_script_arguments(parser: ArgumentParser) -> None:
    parser.add_argument(
        "--actor", help="Only return workflow runs of this user ID."
    )
    parser.add_argument(
        "--branch", help="Only return workflow runs for a specific branch."
    )
    parser.add_argument(
        "--event",
        help="Only return workflow runs triggered by the event specified. "
        "For example, `push`, `pull_request` or `issue`.",
    )
    parser.add_argument(
        "--status",
        help="Only return workflow runs with the status or conclusion "
        "specified.",
    )
    parser.add_argument(
        "--created",
        help="Only returns workflow runs created within the given date-time "
        "range.",
    )
    parser.add_argument("repository")
    parser.add_argument(
        "workflow",
        help="Workflow ID or workflow file name. For example `main.yml`.",
    )


async def github_script(api: GitHubAsyncRESTApi, args: Namespace) -> int:
    table = Table()
    table.add_column("Name")
    table.add_column("ID")
    table.add_column("URL")
    table.add_column("Branch")
    table.add_column("Event")
    table.add_column("Status")
    table.add_column("Updated")
    table.add_column("Actor")

    count = 0
    async for run in api.workflows.get_workflow_runs(
        args.repository,
        args.workflow,
        actor=args.actor,
        branch=args.branch,
        event=args.event,
        status=args.status,
        created=args.created,
    ):
        table.add_row(
            run.name,
            str(run.id),
            f"[link={run.html_url}]{run.html_url}[/link]",
            run.head_branch,
            run.event.value,
            run.conclusion,
            str(run.updated_at),
            run.actor.login if run.actor else "",
        )
        count += 1

    console = Console()
    console.print(table)

    print(f"{count} workflow runs.")
    return 0
