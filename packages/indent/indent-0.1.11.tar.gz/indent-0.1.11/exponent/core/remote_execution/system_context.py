import getpass
import os
import platform

from exponent.core.remote_execution.git import get_git_info
from exponent.core.remote_execution.languages import python_execution
from exponent.core.remote_execution.types import (
    SystemInfo,
)


async def get_system_info(working_directory: str) -> SystemInfo:
    return SystemInfo(
        name=getpass.getuser(),
        cwd=working_directory,
        os=platform.system(),
        shell=_get_user_shell(),
        git=await get_git_info(working_directory),
        python_env=python_execution.get_python_env_info(),
    )


def _get_user_shell() -> str:
    return os.environ.get("SHELL", "bash")
