import json
import logging
import stat
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import (
    Any,
    NoReturn,
    TypeVar,
    cast,
    overload,
)

import websockets
import websockets.exceptions
from anyio import Path as AsyncPath
from bs4 import UnicodeDammit
from httpx import Response
from pydantic import BaseModel
from sentry_sdk.serializer import serialize
from sentry_sdk.utils import (
    event_from_exception,
    exc_info_from_error,
)

from exponent.core.remote_execution.cli_rpc_types import FileMetadata
from exponent.core.remote_execution.types import (
    SUPPORTED_LANGUAGES,
    CLIErrorLog,
    CodeExecutionRequest,
    CodeExecutionResponse,
    CommandRequest,
    CommandResponse,
    CreateCheckpointResponse,
    ErrorResponse,
    FilePath,
    FileWriteRequest,
    FileWriteResponse,
    ListFilesRequest,
    ListFilesResponse,
    RemoteExecutionMessage,
    RemoteExecutionMessageData,
    RemoteExecutionRequest,
    RemoteExecutionRequestType,
    RemoteExecutionResponse,
    RemoteExecutionResponseData,
    RemoteExecutionResponseType,
    RollbackToCheckpointResponse,
    StreamingCodeExecutionResponse,
    StreamingCodeExecutionResponseChunk,
    SupportedLanguage,
)
from exponent.core.types.command_data import NaturalEditContent
from exponent.core.types.event_types import (
    CodeBlockEvent,
    CommandEvent,
    FileWriteEvent,
    LocalEventType,
)
from exponent.utils.version import get_installed_version

logger = logging.getLogger(__name__)

### Serde


def deserialize_response_data(
    response_data: RemoteExecutionResponseData | str,
) -> RemoteExecutionResponseType:
    response: RemoteExecutionResponseType
    if isinstance(response_data, str):
        response_data = RemoteExecutionResponseData.model_validate_json(response_data)
    if response_data.direction != "response":
        raise ValueError(f"Expected response, but got {response_data.direction}")
    if response_data.namespace == "code_execution":
        response = CodeExecutionResponse.model_validate_json(response_data.message_data)
    elif response_data.namespace == "streaming_code_execution":
        response = StreamingCodeExecutionResponse.model_validate_json(
            response_data.message_data
        )
    elif response_data.namespace == "streaming_code_execution_chunk":
        response = StreamingCodeExecutionResponseChunk.model_validate_json(
            response_data.message_data
        )
    elif response_data.namespace == "file_write":
        response = FileWriteResponse.model_validate_json(response_data.message_data)
    elif response_data.namespace == "list_files":
        response = ListFilesResponse.model_validate_json(response_data.message_data)
    elif response_data.namespace == "command":
        response = CommandResponse.model_validate_json(response_data.message_data)
    elif response_data.namespace == "error":
        response = ErrorResponse.model_validate_json(response_data.message_data)
    elif response_data.namespace == "create_checkpoint":
        response = CreateCheckpointResponse.model_validate_json(
            response_data.message_data
        )
    elif response_data.namespace == "rollback_to_checkpoint":
        response = RollbackToCheckpointResponse.model_validate_json(
            response_data.message_data
        )
    else:
        # type checking trick, if you miss a namespace then
        # this won't typecheck due to the input parameter
        # having a potential type other than no-return
        response = assert_unreachable(response_data.namespace)
    return truncate_message(response)


def serialize_message(response: RemoteExecutionMessage) -> str:
    truncated_response = truncate_message(response)
    message = RemoteExecutionMessageData(
        namespace=response.namespace,
        direction=response.direction,
        message_data=truncated_response.model_dump_json(),
    )
    serialized = message.model_dump_json()
    return serialized


### API Serdes


TModel = TypeVar("TModel", bound=BaseModel)


async def deserialize_api_response(
    response: Response,
    data_model: type[TModel],
) -> TModel:
    if response.is_error:
        logging.error(response.text)
        try:
            error_message = response.json()["detail"]
        except Exception:
            error_message = response.text
        raise ValueError(f"{error_message} ({response.status_code})")

    response_json = response.json()
    return data_model.model_validate(response_json)


def get_file_write_content(event: FileWriteEvent) -> str:
    if isinstance(event.write_content, NaturalEditContent):
        assert event.write_content.new_file is not None
        return event.write_content.new_file
    else:
        return event.write_content.content


@overload
def convert_event_to_execution_request(
    request: CodeBlockEvent,
) -> CodeExecutionRequest: ...


@overload
def convert_event_to_execution_request(
    request: FileWriteEvent,
) -> FileWriteRequest: ...


@overload
def convert_event_to_execution_request(
    request: CommandEvent,
) -> CommandRequest: ...


def convert_event_to_execution_request(
    request: LocalEventType,
) -> CodeExecutionRequest | FileWriteRequest | CommandRequest:
    if isinstance(request, CodeBlockEvent):
        language = assert_supported_language(request.language)

        return CodeExecutionRequest(
            language=language,
            content=request.content,
            timeout=request.timeout,
            correlation_id=request.event_uuid,
        )
    elif isinstance(request, FileWriteEvent):
        return FileWriteRequest(
            file_path=request.file_path,
            language=request.language,
            write_strategy=request.write_strategy,
            content=get_file_write_content(request),
            correlation_id=request.event_uuid,
        )
    elif isinstance(request, CommandEvent):
        return CommandRequest(
            data=request.data,
            correlation_id=request.event_uuid,
        )
    else:
        assert_unreachable(request)


### Validation


ResponseT = TypeVar("ResponseT", bound=RemoteExecutionResponse)


def assert_valid_response_type(
    response: RemoteExecutionResponseType, request: RemoteExecutionRequest[ResponseT]
) -> ResponseT | ErrorResponse:
    if isinstance(response, ErrorResponse):
        return response
    if request.namespace != response.namespace or response.direction != "response":
        raise ValueError(
            f"Expected {request.namespace}.response, but got {response.namespace}.{response.direction}"
        )
    return cast(ResponseT, response)


def assert_unreachable(x: NoReturn) -> NoReturn:
    assert False, f"Unhandled type: {type(x).__name__}"


def assert_supported_language(language: str) -> SupportedLanguage:
    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported language: {language}")

    return cast(SupportedLanguage, language)


### Truncation


OUTPUT_CHARACTER_MAX = 90_000  # A tad over ~8k tokens
TRUNCATION_MESSAGE_CHARS = (
    "(Output truncated, only showing the first {remaining_chars} characters)"
)
TRUNCATION_MESSAGE_LINES = (
    "(Output truncated, only showing the first {remaining_lines} lines)"
)
LONGEST_TRUNCATION_MESSAGE_LEN = (
    len(TRUNCATION_MESSAGE_CHARS.format(remaining_chars=OUTPUT_CHARACTER_MAX)) + 1
)

MAX_LINES = 10_000


def truncate_output(
    output: str, character_limit: int = OUTPUT_CHARACTER_MAX
) -> tuple[str, bool]:
    output_length = len(output)
    # When under the character limit, return the output as is.
    # Note we're adding the length of the truncation message + 1
    # to the character limit to account for the fact that the
    # truncation message will be added to the output + a newline.
    # In case we want to run truncation logic both client side
    # and server side, we want to account for the truncation
    # message length to avoid weird double truncation overlap.

    # Attempt to trim whole lines until we're under
    # the character limit.
    lines = output.split("\n")

    if output_length <= character_limit and len(lines) <= MAX_LINES:
        return output, False

    while output_length > character_limit:
        last_line = lines.pop()
        # +1 to account for the newline
        output_length -= len(last_line) + 1

    if not lines:
        # If we truncated all the lines, then we have
        # have some ridiculous long line at the start
        # of the output so we'll just truncate by
        # character count to retain something.
        output = output[:character_limit]
    else:
        # Otherwise, just join the lines back together up to the limit
        lines = lines[:MAX_LINES]
        output = "\n".join(lines)

    return output, True


@overload
def truncate_message(response: CodeExecutionRequest) -> CodeExecutionRequest: ...
@overload
def truncate_message(response: CodeExecutionResponse) -> CodeExecutionResponse: ...
@overload
def truncate_message(
    response: StreamingCodeExecutionResponse,
) -> StreamingCodeExecutionResponse: ...
@overload
def truncate_message(
    response: StreamingCodeExecutionResponseChunk,
) -> StreamingCodeExecutionResponseChunk: ...
@overload
def truncate_message(response: FileWriteRequest) -> FileWriteRequest: ...
@overload
def truncate_message(response: FileWriteResponse) -> FileWriteResponse: ...
@overload
def truncate_message(response: ListFilesRequest) -> ListFilesRequest: ...
@overload
def truncate_message(response: ListFilesResponse) -> ListFilesResponse: ...


@overload
def truncate_message(
    response: RemoteExecutionRequestType,
) -> RemoteExecutionRequestType: ...
@overload
def truncate_message(
    response: RemoteExecutionResponseType,
) -> RemoteExecutionResponseType: ...
@overload
def truncate_message(response: RemoteExecutionMessage) -> RemoteExecutionMessage: ...


def truncate_message(
    response: RemoteExecutionMessage,
) -> RemoteExecutionMessage:
    if isinstance(
        response,
        CodeExecutionResponse
        | StreamingCodeExecutionResponse
        | StreamingCodeExecutionResponseChunk,
    ):
        content, truncated = truncate_output(response.content)
        response.content = content
        if truncated:
            response.truncated = True
    elif (
        isinstance(response, CommandResponse)
        and response.subcommand != "codebase_context"
    ):
        content, truncated = truncate_output(response.content)
        response.content = content
        if truncated:
            response.truncated = True
    return response


### Error Handling


def format_attachment_data(
    attachment_lines: list[str] | None = None,
) -> str | None:
    if not attachment_lines:
        return None
    log_attachment_str = "\n".join(attachment_lines)
    return log_attachment_str


def format_error_log(
    exc: Exception,
    chat_uuid: str | None = None,
    attachment_lines: list[str] | None = None,
) -> CLIErrorLog | None:
    exc_info = exc_info_from_error(exc)
    event, _ = event_from_exception(exc_info)
    attachment_data = format_attachment_data(attachment_lines)
    version = get_installed_version()

    try:
        event_data = json.dumps(serialize(event))  # type: ignore
    except json.JSONDecodeError:
        return None

    return CLIErrorLog(
        event_data=event_data,
        attachment_data=attachment_data,
        version=version,
        chat_uuid=chat_uuid,
    )


### Websockets


ws_logger = logging.getLogger("WebsocketUtils")


def ws_retry(
    connection_name: str,
    max_retries: int = 5,
) -> Callable[[Callable[..., Awaitable[None]]], Callable[..., Awaitable[None]]]:
    connection_name = connection_name.capitalize()
    reconnect_msg = f"{connection_name} reconnecting."
    disconnect_msg = f"{connection_name} connection closed."
    max_disconnect_msg = (
        f"{connection_name} connection closed {max_retries} times, exiting."
    )

    def decorator(
        f: Callable[..., Awaitable[None]],
    ) -> Callable[..., Awaitable[None]]:
        @wraps(f)
        async def wrapped(*args: Any, **kwargs: Any) -> None:
            i = 0

            while True:
                try:
                    return await f(*args, **kwargs)
                except (websockets.exceptions.ConnectionClosed, TimeoutError) as e:
                    # Warn on disconnect
                    ws_logger.warning(disconnect_msg)

                    if i >= max_retries:
                        # We've reached the max number of retries,
                        # log an error and reraise
                        ws_logger.warning(max_disconnect_msg)
                        raise e

                    # Increment the retry count
                    i += 1
                    # Notify the user that we're reconnecting
                    ws_logger.warning(reconnect_msg)
                    continue

        return wrapped

    return decorator


async def safe_read_file(path: FilePath) -> str:
    path = AsyncPath(path)

    try:
        return await path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        # Potentially a wacky encoding or mixture of encodings,
        # attempt to correct it.
        fbytes = await path.read_bytes()
        # Handles mixed encodings with utf-8 and cp1252 (windows)
        fbytes = UnicodeDammit.detwingle(fbytes)

        decode_result = smart_decode(fbytes)

        if decode_result:
            # First item in tuple is the decoded str
            return decode_result[0]

        raise


async def safe_get_file_metadata(path: FilePath) -> FileMetadata | None:
    path = AsyncPath(path)
    try:
        stats = await path.stat()
    except Exception as e:
        logger.error(f"Error getting file metadata: {e!s}")
        return None

    return FileMetadata(
        modified_timestamp=stats.st_mtime,
        file_mode=stat.filemode(stats.st_mode),
    )


async def safe_write_file(path: FilePath, content: str) -> None:
    await AsyncPath(path).write_text(content, encoding="utf-8")


def smart_decode(b: bytes) -> tuple[str, str] | None:
    # This function attempts to decode by detecting the actual source
    # encoding, returning (decoded_str, detected_encoding) if successful.
    # We also attempt to fix cases of mixed encodings of cp1252 + utf-8
    # using the detwingle helper provided by bs4. This can happen on
    # windows, particularly when a user edits a utf-8 file by pasting in
    # the special windows smart quotes.
    b = UnicodeDammit.detwingle(b)

    encoding = UnicodeDammit(
        b, known_definite_encodings=["utf-8", "cp1252"]
    ).original_encoding

    if not encoding:
        return None

    return (b.decode(encoding=encoding), encoding)
