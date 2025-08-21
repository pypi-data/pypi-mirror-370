import logging
import uuid
from collections.abc import Callable
from pathlib import Path
from time import time

from anyio import Path as AsyncPath

from exponent.core.remote_execution import files
from exponent.core.remote_execution.cli_rpc_types import (
    BashToolInput,
    BashToolResult,
    EditToolInput,
    EditToolResult,
    ErrorToolResult,
    GlobToolInput,
    GlobToolResult,
    GrepToolInput,
    GrepToolResult,
    ListToolInput,
    ListToolResult,
    ReadToolInput,
    ReadToolResult,
    ToolInputType,
    ToolResultType,
    WriteToolInput,
    WriteToolResult,
)
from exponent.core.remote_execution.code_execution import (
    execute_code_streaming,
)
from exponent.core.remote_execution.file_write import execute_full_file_rewrite
from exponent.core.remote_execution.truncation import truncate_tool_result
from exponent.core.remote_execution.types import (
    StreamingCodeExecutionRequest,
    StreamingCodeExecutionResponse,
)
from exponent.core.remote_execution.utils import (
    assert_unreachable,
    safe_get_file_metadata,
    safe_read_file,
)

logger = logging.getLogger(__name__)


async def execute_tool(
    tool_input: ToolInputType, working_directory: str
) -> ToolResultType:
    if isinstance(tool_input, ReadToolInput):
        return await execute_read_file(tool_input, working_directory)
    elif isinstance(tool_input, WriteToolInput):
        return await execute_write_file(tool_input, working_directory)
    elif isinstance(tool_input, ListToolInput):
        return await execute_list_files(tool_input, working_directory)
    elif isinstance(tool_input, GlobToolInput):
        return await execute_glob_files(tool_input, working_directory)
    elif isinstance(tool_input, GrepToolInput):
        return await execute_grep_files(tool_input, working_directory)
    elif isinstance(tool_input, EditToolInput):
        return await execute_edit_file(tool_input, working_directory)
    elif isinstance(tool_input, BashToolInput):
        raise ValueError("Bash tool input should be handled by execute_bash_tool")
    else:
        assert_unreachable(tool_input)


def truncate_result[T: ToolResultType](tool_result: T) -> T:
    return truncate_tool_result(tool_result)


async def execute_read_file(  # noqa: PLR0911
    tool_input: ReadToolInput, working_directory: str
) -> ReadToolResult | ErrorToolResult:
    # Validate absolute path requirement
    if not tool_input.file_path.startswith("/"):
        return ErrorToolResult(
            error_message=f"File path must be absolute, got relative path: {tool_input.file_path}"
        )

    # Validate offset and limit
    offset = tool_input.offset if tool_input.offset is not None else 0
    limit = tool_input.limit if tool_input.limit is not None else 2000

    if offset < 0:
        return ErrorToolResult(
            error_message=f"Offset must be non-negative, got: {offset}"
        )

    if limit <= 0:
        return ErrorToolResult(error_message=f"Limit must be positive, got: {limit}")

    file = AsyncPath(working_directory, tool_input.file_path)

    try:
        exists = await file.exists()
    except (OSError, PermissionError) as e:
        return ErrorToolResult(error_message=f"Cannot access file: {e!s}")

    if not exists:
        return ErrorToolResult(
            error_message="File not found",
        )

    try:
        if await file.is_dir():
            return ErrorToolResult(
                error_message=f"{await file.absolute()} is a directory",
            )
    except (OSError, PermissionError) as e:
        return ErrorToolResult(error_message=f"Cannot check file type: {e!s}")

    try:
        content = await safe_read_file(file)
    except PermissionError:
        return ErrorToolResult(
            error_message=f"Permission denied: cannot read {tool_input.file_path}"
        )
    except UnicodeDecodeError:
        return ErrorToolResult(
            error_message="File appears to be binary or has invalid text encoding"
        )
    except Exception as e:
        return ErrorToolResult(error_message=f"Error reading file: {e!s}")

    metadata = await safe_get_file_metadata(file)

    # Handle empty files
    if not content:
        return ReadToolResult(
            content="",
            num_lines=0,
            start_line=0,
            total_lines=0,
            metadata=metadata,
        )

    content_lines = content.splitlines(keepends=True)
    total_lines = len(content_lines)

    # Handle offset beyond file length
    if offset >= total_lines:
        return ReadToolResult(
            content="",
            num_lines=0,
            start_line=offset,
            total_lines=total_lines,
            metadata=metadata,
        )

    # Apply offset and limit
    content_lines = content_lines[offset : offset + limit]

    # Apply character-level truncation at line boundaries to ensure consistency
    # This ensures the content field and num_lines field remain in sync
    CHARACTER_LIMIT = 90_000  # Match the limit in truncation.py

    # Join lines and check total size
    final_content = "".join(content_lines)

    if len(final_content) > CHARACTER_LIMIT:
        # Truncate at line boundaries to stay under the limit
        truncated_lines: list[str] = []
        current_size = 0
        truncation_message = "\n[Content truncated due to size limit]"
        truncation_size = len(truncation_message)
        lines_included = 0

        for line in content_lines:
            # Check if adding this line would exceed the limit (accounting for truncation message)
            if current_size + len(line) + truncation_size > CHARACTER_LIMIT:
                final_content = "".join(truncated_lines) + truncation_message
                break
            truncated_lines.append(line)
            current_size += len(line)
            lines_included += 1
        else:
            # All lines fit (shouldn't happen if we got here, but be safe)
            final_content = "".join(truncated_lines)
            lines_included = len(content_lines)

        num_lines = lines_included
    else:
        num_lines = len(content_lines)

    return ReadToolResult(
        content=final_content,
        num_lines=num_lines,
        start_line=offset,
        total_lines=total_lines,
        metadata=metadata,
    )


async def execute_write_file(
    tool_input: WriteToolInput, working_directory: str
) -> WriteToolResult:
    file_path = tool_input.file_path
    path = Path(working_directory, file_path)
    result = await execute_full_file_rewrite(
        path, tool_input.content, working_directory
    )
    return WriteToolResult(message=result)


async def execute_edit_file(  # noqa: PLR0911
    tool_input: EditToolInput, working_directory: str
) -> EditToolResult | ErrorToolResult:
    # Validate absolute path requirement
    if not tool_input.file_path.startswith("/"):
        return ErrorToolResult(
            error_message=f"File path must be absolute, got relative path: {tool_input.file_path}"
        )

    file = AsyncPath(working_directory, tool_input.file_path)

    try:
        exists = await file.exists()
    except (OSError, PermissionError) as e:
        return ErrorToolResult(error_message=f"Cannot access file: {e!s}")

    if not exists:
        return ErrorToolResult(error_message="File not found")

    if tool_input.last_known_modified_timestamp is not None:
        metadata = await safe_get_file_metadata(file)
        if (
            metadata is not None
            and metadata.modified_timestamp > tool_input.last_known_modified_timestamp
        ):
            return ErrorToolResult(
                error_message="File has been modified since last read/write"
            )

    try:
        if await file.is_dir():
            return ErrorToolResult(
                error_message=f"{await file.absolute()} is a directory"
            )
    except (OSError, PermissionError) as e:
        return ErrorToolResult(error_message=f"Cannot check file type: {e!s}")

    try:
        # Read the entire file without truncation limits
        content = await safe_read_file(file)
    except PermissionError:
        return ErrorToolResult(
            error_message=f"Permission denied: cannot read {tool_input.file_path}"
        )
    except UnicodeDecodeError:
        return ErrorToolResult(
            error_message="File appears to be binary or has invalid text encoding"
        )
    except Exception as e:
        return ErrorToolResult(error_message=f"Error reading file: {e!s}")

    # Check if search text exists
    if tool_input.old_string not in content:
        return ErrorToolResult(
            error_message=f"Search text not found in {tool_input.file_path}"
        )

    # Check if old_string and new_string are identical
    if tool_input.old_string == tool_input.new_string:
        return ErrorToolResult(error_message="Old string and new string are identical")

    # Check uniqueness if replace_all is False
    if not tool_input.replace_all:
        occurrences = content.count(tool_input.old_string)
        if occurrences > 1:
            return ErrorToolResult(
                error_message=f"String '{tool_input.old_string}' appears {occurrences} times in file. Use a larger context or replace_all=True"
            )

    # Perform replacement
    if tool_input.replace_all:
        new_content = content.replace(tool_input.old_string, tool_input.new_string)
    else:
        # Replace only the first occurrence
        new_content = content.replace(tool_input.old_string, tool_input.new_string, 1)

    # Write back to file
    try:
        path = Path(working_directory, tool_input.file_path)
        await execute_full_file_rewrite(path, new_content, working_directory)
        return EditToolResult(
            message=f"Successfully replaced text in {tool_input.file_path}",
            metadata=await safe_get_file_metadata(path),
        )
    except Exception as e:
        return ErrorToolResult(error_message=f"Error writing file: {e!s}")


async def execute_list_files(
    tool_input: ListToolInput, working_directory: str
) -> ListToolResult | ErrorToolResult:
    path = AsyncPath(tool_input.path)

    try:
        exists = await path.exists()
    except (OSError, PermissionError) as e:
        return ErrorToolResult(error_message=f"Cannot access path: {e!s}")

    if not exists:
        return ErrorToolResult(error_message=f"Directory not found: {tool_input.path}")

    try:
        is_dir = await path.is_dir()
    except (OSError, PermissionError) as e:
        return ErrorToolResult(
            error_message=f"Cannot check if path is directory: {e!s}"
        )

    if not is_dir:
        return ErrorToolResult(
            error_message=f"Path is not a directory: {tool_input.path}"
        )

    try:
        filenames = [entry.name async for entry in path.iterdir()]
    except (OSError, PermissionError) as e:
        return ErrorToolResult(error_message=f"Cannot list directory contents: {e!s}")

    return ListToolResult(
        files=[filename for filename in filenames],
    )


async def execute_glob_files(
    tool_input: GlobToolInput, working_directory: str
) -> GlobToolResult:
    # async timer
    start_time = time()
    results = await files.glob(
        path=working_directory if tool_input.path is None else tool_input.path,
        glob_pattern=tool_input.pattern,
    )
    duration_ms = int((time() - start_time) * 1000)
    return GlobToolResult(
        filenames=results,
        duration_ms=duration_ms,
        num_files=len(results),
        truncated=len(results) >= files.GLOB_MAX_COUNT,
    )


async def execute_grep_files(
    tool_input: GrepToolInput, working_directory: str
) -> GrepToolResult | ErrorToolResult:
    return await files.search_files(
        path_str=working_directory if tool_input.path is None else tool_input.path,
        file_pattern=tool_input.include,
        regex=tool_input.pattern,
        working_directory=working_directory,
        multiline=tool_input.multiline,
    )


async def execute_bash_tool(
    tool_input: BashToolInput, working_directory: str, should_halt: Callable[[], bool]
) -> BashToolResult:
    start_time = time()
    result = None
    async for result in execute_code_streaming(
        StreamingCodeExecutionRequest(
            language="shell",
            content=tool_input.command,
            timeout=120 if tool_input.timeout is None else tool_input.timeout,
            correlation_id=str(uuid.uuid4()),
        ),
        working_directory=working_directory,
        session=None,  # type: ignore
        should_halt=should_halt,
    ):
        pass

    assert isinstance(result, StreamingCodeExecutionResponse)

    return BashToolResult(
        shell_output=result.content,
        exit_code=result.exit_code,
        duration_ms=int((time() - start_time) * 1000),
        timed_out=result.cancelled_for_timeout,
        stopped_by_user=result.halted,
    )
