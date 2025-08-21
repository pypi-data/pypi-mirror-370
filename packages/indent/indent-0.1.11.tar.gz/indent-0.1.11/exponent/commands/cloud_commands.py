import asyncio
import sys

import click

from exponent.commands.common import (
    check_inside_git_repo,
    check_running_from_home_directory,
    check_ssl,
    create_cloud_chat,
    redirect_to_login,
    start_chat_turn,
)
from exponent.commands.settings import use_settings
from exponent.commands.types import exponent_cli_group
from exponent.commands.utils import (
    launch_exponent_browser,
    print_exponent_message,
)
from exponent.core.config import Settings
from exponent.utils.version import check_exponent_version_and_upgrade


@exponent_cli_group(hidden=True)
def cloud_cli() -> None:
    pass


@cloud_cli.command(hidden=True)
@click.option(
    "--cloud-config-id",
    help="ID of an existing cloud config to reconnect",
    required=True,
)
@click.option(
    "--prompt",
    help="Prompt to kick off the cloud session.",
    required=True,
)
@click.option(
    "--background",
    "-b",
    help="Start the cloud session without launching the Exponent UI",
    is_flag=True,
    default=False,
)
@use_settings
def cloud(
    settings: Settings,
    cloud_config_id: str,
    prompt: str,
    background: bool,
) -> None:
    check_exponent_version_and_upgrade(settings)

    if not settings.api_key:
        redirect_to_login(settings)
        return

    loop = asyncio.get_event_loop()

    check_running_from_home_directory()
    loop.run_until_complete(check_inside_git_repo(settings))
    check_ssl()

    api_key = settings.api_key
    base_url = settings.base_url
    base_api_url = settings.get_base_api_url()
    base_ws_url = settings.get_base_ws_url()

    chat_uuid = loop.run_until_complete(
        create_cloud_chat(api_key, base_api_url, base_ws_url, cloud_config_id)
    )

    if chat_uuid is None:
        sys.exit(1)

    loop.run_until_complete(
        start_chat_turn(api_key, base_api_url, base_ws_url, chat_uuid, prompt)
    )

    print_exponent_message(base_url, chat_uuid)

    if not background:
        launch_exponent_browser(settings.environment, base_url, chat_uuid)
