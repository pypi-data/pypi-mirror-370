import asyncio
import sys
import time

import click

from exponent.commands.common import (
    check_inside_git_repo,
    check_running_from_home_directory,
    check_ssl,
    create_chat,
    inside_ssh_session,
    redirect_to_login,
    start_client,
)
from exponent.commands.settings import use_settings
from exponent.commands.types import exponent_cli_group
from exponent.commands.utils import (
    ConnectionTracker,
    Spinner,
    launch_exponent_browser,
    print_exponent_message,
)
from exponent.core.config import Settings
from exponent.core.remote_execution.client import (
    REMOTE_EXECUTION_CLIENT_EXIT_INFO,
    SwitchCLIChat,
    WSDisconnected,
)
from exponent.core.remote_execution.types import ChatSource
from exponent.core.remote_execution.utils import assert_unreachable
from exponent.utils.version import check_exponent_version_and_upgrade

try:
    # this is an optional dependency for python <3.11
    from async_timeout import timeout
except ImportError:  # pragma: no cover
    from asyncio import timeout


@exponent_cli_group()
def run_cli() -> None:
    """Run AI-powered chat sessions."""
    pass


@run_cli.command()
@click.option(
    "--chat-id",
    help="ID of an existing chat session to reconnect",
    required=False,
    prompt_required=False,
    prompt="Enter the chat ID to reconnect to",
)
@click.option(
    "--prompt",
    help="Start a chat with a given prompt.",
)
@click.option(
    "--workflow-id",
    hidden=True,
    required=False,
)
@use_settings
def run(
    settings: Settings,
    chat_id: str | None = None,
    prompt: str | None = None,
    workflow_id: str | None = None,
) -> None:
    """[default] Start or reconnect to an Indent session."""
    check_exponent_version_and_upgrade(settings)

    if not settings.api_key:
        redirect_to_login(settings)
        return

    loop = asyncio.get_event_loop()

    check_running_from_home_directory()
    check_ssl()
    loop.run_until_complete(check_inside_git_repo(settings))

    api_key = settings.api_key
    base_url = settings.base_url
    base_api_url = settings.get_base_api_url()
    base_ws_url = settings.get_base_ws_url()

    chat_uuid = chat_id or loop.run_until_complete(
        create_chat(api_key, base_api_url, base_ws_url, ChatSource.CLI_RUN)
    )

    if chat_uuid is None:
        sys.exit(1)

    if (
        not prompt
        and (not inside_ssh_session())
        and (not workflow_id)
        # If the user specified a chat ID, they probably don't want to re-launch the chat
        and (not chat_id)
    ):
        # Open the chat in the browser
        launch_exponent_browser(settings.environment, base_url, chat_uuid)

    while True:
        result = run_chat(loop, api_key, chat_uuid, settings, prompt, workflow_id)
        if result is None or isinstance(result, WSDisconnected):
            # NOTE: None here means that handle_connection_changes exited
            # first. We should likely have a different message for this.
            if result and result.error_message:
                click.secho(f"Error: {result.error_message}", fg="red")
                sys.exit(10)
            else:
                print("Disconnected upon user request, shutting down...")
                break
        elif isinstance(result, SwitchCLIChat):
            chat_uuid = result.new_chat_uuid
            print("\nSwitching chats...")
        else:
            assert_unreachable(result)


def run_chat(
    loop: asyncio.AbstractEventLoop,
    api_key: str,
    chat_uuid: str,
    settings: Settings,
    prompt: str | None,
    workflow_id: str | None,
) -> REMOTE_EXECUTION_CLIENT_EXIT_INFO | None:
    start_ts = time.time()
    base_url = settings.base_url
    base_api_url = settings.get_base_api_url()
    base_ws_url = settings.get_base_ws_url()

    print_exponent_message(base_url, chat_uuid)
    print()

    connection_tracker = ConnectionTracker()

    client_fut = loop.create_task(
        start_client(
            api_key,
            base_url,
            base_api_url,
            base_ws_url,
            chat_uuid,
            prompt=prompt,
            workflow_id=workflow_id,
            connection_tracker=connection_tracker,
        )
    )

    conn_fut = loop.create_task(handle_connection_changes(connection_tracker, start_ts))

    try:
        done, _ = loop.run_until_complete(
            asyncio.wait({client_fut, conn_fut}, return_when=asyncio.FIRST_COMPLETED)
        )

        if client_fut in done:
            return client_fut.result()
        else:
            return None
    finally:
        for task in asyncio.all_tasks(loop):
            task.cancel()

        try:
            loop.run_until_complete(asyncio.wait(asyncio.all_tasks(loop)))
        except asyncio.CancelledError:
            pass


async def handle_connection_changes(
    connection_tracker: ConnectionTracker, start_ts: float
) -> None:
    try:
        async with timeout(5):
            assert await connection_tracker.next_change()
            print(ready_message(start_ts))
    except TimeoutError:
        spinner = Spinner("Connecting...")
        spinner.show()
        assert await connection_tracker.next_change()
        spinner.hide()
        print(ready_message(start_ts))

    while True:
        assert not await connection_tracker.next_change()

        print("Disconnected...", end="")
        await asyncio.sleep(1)
        spinner = Spinner("Reconnecting...")
        spinner.show()
        assert await connection_tracker.next_change()
        spinner.hide()
        print("\x1b[1;32m✓ Reconnected", end="")
        sys.stdout.flush()
        await asyncio.sleep(1)
        print("\r\x1b[0m\x1b[2K", end="")
        sys.stdout.flush()


def ready_message(start_ts: float) -> str:
    elapsed = round(time.time() - start_ts, 2)
    return f"\x1b[32m✓\x1b[0m Ready in {elapsed}s"
