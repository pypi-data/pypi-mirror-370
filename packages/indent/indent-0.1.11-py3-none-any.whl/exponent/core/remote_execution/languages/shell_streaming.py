import asyncio
import os
import platform
import shutil
import signal
from collections.abc import AsyncGenerator, Callable
from typing import Any

from exponent.core.remote_execution.languages.types import (
    ShellExecutionResult,
    StreamedOutputPiece,
)
from exponent.core.remote_execution.utils import smart_decode

STDOUT_FD = 1
STDERR_FD = 2
MAX_TIMEOUT = 300


def get_rc_file_source_command(shell_path: str) -> str:
    """
    Returns a command to source the user's shell rc file
    Login profiles are already sourced via the -l flag
    """
    # On Windows, shell behavior is different
    if platform.system() == "Windows":
        return ""  # Windows shells don't typically use rc files in the same way

    shell_name = os.path.basename(shell_path)
    home_dir = os.path.expanduser("~")

    if shell_name == "zsh":
        zshrc = os.path.join(home_dir, ".zshrc")
        if os.path.exists(zshrc):
            return f"source {zshrc} 2>/dev/null || true; "
    elif shell_name == "bash":
        bashrc = os.path.join(home_dir, ".bashrc")
        if os.path.exists(bashrc):
            return f"source {bashrc} 2>/dev/null || true; "

    return ""  # No rc file found or unsupported shell


async def read_stream(
    stream: asyncio.StreamReader, fd: int, output: list[tuple[int, str]]
) -> AsyncGenerator[StreamedOutputPiece, None]:
    data: bytes = b""
    encoding = "utf-8"

    while True:
        try:
            data = await stream.read(4096)
            if not data:
                break
            chunk = data.decode(encoding=encoding)
            output.append((fd, chunk))
            yield StreamedOutputPiece(content=chunk)
        except UnicodeDecodeError:
            decode_result = smart_decode(data)

            if decode_result is None:
                break

            # Store the detected encoding as a hint for how
            # to decode the remaining chunks of data
            chunk, encoding = decode_result

            output.append((fd, chunk))
            yield StreamedOutputPiece(content=chunk)

            continue
        except asyncio.CancelledError:
            raise
        except Exception:
            break


async def execute_shell_streaming(  # noqa: PLR0915
    code: str,
    working_directory: str,
    timeout: int,
    should_halt: Callable[[], bool] | None = None,
) -> AsyncGenerator[StreamedOutputPiece | ShellExecutionResult, None]:
    timeout_seconds = min(timeout, MAX_TIMEOUT)

    shell_path = os.environ.get("SHELL") or shutil.which("bash") or shutil.which("sh")

    if not shell_path:
        process = await asyncio.create_subprocess_shell(
            code,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=working_directory,
        )
    else:
        # Add rc file sourcing to the command
        rc_source_cmd = get_rc_file_source_command(shell_path)
        full_command = f"{rc_source_cmd}{code}"

        process = await asyncio.create_subprocess_exec(
            shell_path,
            "-l",
            "-c",
            full_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=working_directory,
            start_new_session=True if platform.system() != "Windows" else False,
        )

    exit_code = None
    output: list[tuple[int, str]] = []
    halted = False
    timed_out = False
    assert process.stdout
    assert process.stderr

    async def monitor_halt() -> None:
        nonlocal halted

        while True:
            if should_halt and should_halt():
                # Send signal to process group for proper interrupt propagation
                try:
                    if platform.system() != "Windows":
                        # Send SIGTERM to the process group
                        os.killpg(process.pid, signal.SIGTERM)
                        try:
                            await asyncio.wait_for(process.wait(), timeout=2.0)
                        except TimeoutError:
                            # Fall back to SIGKILL to process group
                            os.killpg(process.pid, signal.SIGKILL)
                    else:
                        # Windows fallback
                        process.terminate()
                        try:
                            await asyncio.wait_for(process.wait(), timeout=2.0)
                        except TimeoutError:
                            process.kill()
                except (ProcessLookupError, OSError):
                    # Process or process group already terminated
                    pass
                halted = True
                break
            if process.returncode is not None:
                break
            await asyncio.sleep(0.1)

    def on_timeout() -> None:
        nonlocal timed_out
        timed_out = True
        process.kill()

    try:
        halt_task = asyncio.create_task(monitor_halt()) if should_halt else None
        timeout_handle = asyncio.get_running_loop().call_later(
            timeout_seconds, on_timeout
        )

        # Stream stdout and stderr concurrently using wait
        stdout_gen = read_stream(process.stdout, STDOUT_FD, output)
        stderr_gen = read_stream(process.stderr, STDERR_FD, output)

        stdout_task = asyncio.create_task(stdout_gen.__anext__())
        stderr_task = asyncio.create_task(stderr_gen.__anext__())
        pending = {stdout_task, stderr_task}

        while pending:
            done, pending = await asyncio.wait(
                pending, return_when=asyncio.FIRST_COMPLETED
            )

            for task in done:
                try:
                    piece = await task
                    yield piece

                    if process.returncode is not None:
                        break

                    # Schedule next read from the same stream
                    if task is stdout_task and not process.stdout.at_eof():
                        stdout_task = asyncio.create_task(stdout_gen.__anext__())
                        pending.add(stdout_task)
                    elif task is stderr_task and not process.stderr.at_eof():
                        stderr_task = asyncio.create_task(stderr_gen.__anext__())
                        pending.add(stderr_task)
                except StopAsyncIteration:
                    continue

        exit_code = await process.wait()
        timeout_handle.cancel()

    except asyncio.CancelledError:
        process.kill()
        raise
    finally:
        # Explicitly kill the process if it's still running
        if process and process.returncode is None:
            try:
                if platform.system() != "Windows":
                    os.killpg(process.pid, signal.SIGTERM)
                else:
                    process.terminate()
            except (ProcessLookupError, OSError):
                pass

        tasks_to_cancel: list[asyncio.Task[Any]] = [stdout_task, stderr_task]
        if halt_task:
            tasks_to_cancel.append(halt_task)

        await asyncio.gather(*tasks_to_cancel, return_exceptions=True)

    formatted_output = "".join([chunk for (_, chunk) in output]).strip() + "\n\n"

    yield ShellExecutionResult(
        output=formatted_output,
        cancelled_for_timeout=timed_out,
        exit_code=None if timed_out else exit_code,
        halted=halted,
    )
