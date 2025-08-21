from collections.abc import AsyncGenerator, Callable

from exponent.core.remote_execution.languages.python_execution import (
    execute_python_streaming,
)
from exponent.core.remote_execution.languages.shell_streaming import (
    execute_shell_streaming,
)
from exponent.core.remote_execution.languages.types import StreamedOutputPiece
from exponent.core.remote_execution.session import RemoteExecutionClientSession
from exponent.core.remote_execution.types import (
    StreamingCodeExecutionRequest,
    StreamingCodeExecutionResponse,
    StreamingCodeExecutionResponseChunk,
)

EMPTY_OUTPUT_STRING = "(No output)"


async def execute_code_streaming(
    request: StreamingCodeExecutionRequest,
    session: RemoteExecutionClientSession,
    working_directory: str,
    should_halt: Callable[[], bool] | None = None,
) -> AsyncGenerator[
    StreamingCodeExecutionResponseChunk | StreamingCodeExecutionResponse, None
]:
    if request.language == "python":
        async for output in execute_python_streaming(
            request.content, session.kernel, user_interrupted=should_halt
        ):
            if isinstance(output, StreamedOutputPiece):
                yield StreamingCodeExecutionResponseChunk(
                    content=output.content, correlation_id=request.correlation_id
                )
            else:
                yield StreamingCodeExecutionResponse(
                    correlation_id=request.correlation_id,
                    content=output.output or EMPTY_OUTPUT_STRING,
                    halted=output.halted,
                )

    elif request.language == "shell":
        async for shell_output in execute_shell_streaming(
            request.content, working_directory, request.timeout, should_halt
        ):
            if isinstance(shell_output, StreamedOutputPiece):
                yield StreamingCodeExecutionResponseChunk(
                    content=shell_output.content, correlation_id=request.correlation_id
                )
            else:
                yield StreamingCodeExecutionResponse(
                    correlation_id=request.correlation_id,
                    content=shell_output.output or EMPTY_OUTPUT_STRING,
                    halted=shell_output.halted,
                    exit_code=shell_output.exit_code,
                    cancelled_for_timeout=shell_output.cancelled_for_timeout,
                )
