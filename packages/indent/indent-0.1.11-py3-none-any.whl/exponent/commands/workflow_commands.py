import asyncio
import os
import sys
from typing import cast

import click

from exponent.commands.run_commands import run_chat
from exponent.commands.settings import use_settings
from exponent.commands.types import exponent_cli_group
from exponent.core.config import Settings
from exponent.core.remote_execution.client import RemoteExecutionClient, WSDisconnected
from exponent.core.remote_execution.types import (
    PrReviewWorkflowInput,
    WorkflowTriggerResponse,
)


@exponent_cli_group(name="workflow")
def workflow_cli() -> None:
    """Workflow commands."""
    pass


@workflow_cli.group(hidden=True)
def workflow() -> None:
    """Workflow management commands."""
    pass


@workflow.command()
@use_settings
@click.argument("workflow_type", type=click.STRING)
def trigger(settings: Settings, workflow_type: str) -> None:
    """Trigger a workflow."""

    if not settings.api_key:
        raise click.ClickException(
            "No API key found. Use `indent login` to set your API key."
        )

    if workflow_type != "pr_review":
        raise click.UsageError("Invalid workflow name. Only 'pr_review' is supported.")

    loop = asyncio.get_event_loop()
    response = loop.run_until_complete(trigger_pr_review_workflow(settings))

    while True:
        result = run_chat(
            loop, settings.api_key, response.chat_uuid, settings, None, None
        )
        if result is None or isinstance(result, WSDisconnected):
            # NOTE: None here means that handle_connection_changes exited
            # first. We should likely have a different message for this.
            if result and result.error_message:
                click.secho(f"Error: {result.error_message}", fg="red")
                sys.exit(10)
            else:
                click.echo("Disconnected upon user request, shutting down...")
                break
        else:
            raise click.ClickException("Workflow run exited unexpectedly")


async def _subprocess_check_output(command: str) -> str:
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )
    stdout, _ = await process.communicate()

    if process.returncode != 0:
        output = stdout.decode().strip()
        raise click.ClickException(
            f"Command '{command}' failed with exit code {process.returncode}:\n{output}"
        )

    return stdout.decode().strip()


async def trigger_pr_review_workflow(settings: Settings) -> WorkflowTriggerResponse:
    origin_url = await _subprocess_check_output("git ls-remote --get-url origin")
    url = origin_url.strip().removesuffix(".git")
    remote = url.split(":")[-1]
    owner, repo = remote.split("/")[-2:]

    pr_number_str = os.environ.get("PR_NUMBER")
    if not pr_number_str:
        raise click.ClickException("PR_NUMBER environment variable is not set")
    try:
        pr_number = int(pr_number_str)
    except ValueError:
        raise click.ClickException(
            "PR_NUMBER environment variable is not a valid integer"
        )

    async with RemoteExecutionClient.session(
        api_key=cast(str, settings.api_key),
        base_url=settings.get_base_api_url(),
        base_ws_url=settings.get_base_ws_url(),
        working_directory=os.getcwd(),
    ) as client:
        return await client.trigger_workflow(
            workflow_name="pr_review",
            workflow_input=PrReviewWorkflowInput(
                repo_owner=owner,
                repo_name=repo,
                pr_number=pr_number,
            ),
        )
