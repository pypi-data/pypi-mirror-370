import datetime
import json
from enum import Enum
from functools import cached_property
from os import PathLike
from pathlib import Path, PurePath
from typing import (
    Annotated,
    Any,
    ClassVar,
    Generic,
    Literal,
    TypeVar,
)

from anyio import Path as AsyncPath
from pydantic import BaseModel, Field

from exponent.core.remote_execution.error_info import SerializableErrorInfo
from exponent.core.types.command_data import (
    CommandDataType,
    FileWriteStrategyName,
)

type FilePath = str | PathLike[str]


# DEPRECATED, only around for gql compatibility
class UseToolsMode(str, Enum):
    read_only = "read_only"
    read_write = "read_write"
    disabled = "disabled"


class CreateChatResponse(BaseModel):
    chat_uuid: str


class RunWorkflowRequest(BaseModel):
    chat_uuid: str
    workflow_id: str


# note: before adding fields here, probably update
# get_workflow_run_by_trigger db query
class PrReviewWorkflowInput(BaseModel):
    repo_owner: str
    repo_name: str
    pr_number: int


class WorkflowTriggerRequest(BaseModel):
    workflow_name: str
    workflow_input: PrReviewWorkflowInput


class WorkflowTriggerResponse(BaseModel):
    chat_uuid: str


class ExecutionEndResponse(BaseModel):
    execution_ended: bool


class SignalType(str, Enum):
    disconnect = "disconnect"

    def __str__(self) -> str:
        return self.value


class GitInfo(BaseModel):
    branch: str
    remote: str | None


class PythonEnvInfo(BaseModel):
    interpreter_path: str | None
    interpreter_version: str | None
    name: str | None = "exponent"
    provider: Literal["venv", "pyenv", "pipenv", "conda"] | None = "pyenv"


class SystemInfo(BaseModel):
    name: str
    cwd: str
    os: str
    shell: str
    git: GitInfo | None
    python_env: PythonEnvInfo | None


class HeartbeatInfo(BaseModel):
    exponent_version: str | None = None
    editable_installation: bool = False
    system_info: SystemInfo | None
    timestamp: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
    )
    timestamp_received: datetime.datetime | None = None


class RemoteFile(BaseModel):
    file_path: str
    working_directory: str = "."

    @cached_property
    def pure_path(self) -> PurePath:
        return PurePath(self.working_directory, self.file_path)

    @cached_property
    def path(self) -> Path:
        return Path(self.working_directory, self.file_path)

    @cached_property
    def name(self) -> str:
        return self.pure_path.name

    @cached_property
    def absolute_path(self) -> str:
        return self.path.absolute().as_posix()

    async def resolve(self, client_working_directory: str) -> str:
        working_directory = AsyncPath(self.working_directory, self.file_path)

        if not working_directory.is_absolute():
            working_directory = AsyncPath(client_working_directory, working_directory)

        return str(await working_directory.resolve())

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RemoteFile):
            return False

        return self.path.name == other.path.name

    def __lt__(self, other: "RemoteFile") -> bool:
        # Prefer shorter paths
        if (cmp := self._cmp_path_len(other)) is not None:
            return cmp

        # Prefer paths sorted by parent directory
        if (cmp := self._cmp_path_str(other)) is not None:
            return cmp

        # Prefer paths with alphabetical first character
        return self._cmp_first_char(other)

    def __hash__(self) -> int:
        return hash(self.absolute_path)

    def _cmp_first_char(self, other: "RemoteFile") -> bool:
        return self._cmp_str(self.path.name, other.path.name)

    def _cmp_path_len(self, other: "RemoteFile") -> bool | None:
        self_parts = self.path.absolute().parent.parts
        other_parts = other.path.absolute().parent.parts

        if len(self_parts) == len(other_parts):
            return None

        return len(self_parts) < len(other_parts)

    def _cmp_path_str(self, other: "RemoteFile") -> bool | None:
        self_parts = self.path.absolute().parent.parts
        other_parts = other.path.absolute().parent.parts

        if self_parts == other_parts:
            return None

        for a, b in zip(self_parts, other_parts):
            if a != b:
                return self._cmp_str(a, b)

        return False

    @staticmethod
    def _cmp_str(s1: str, s2: str) -> bool:
        if s1[:1].isalpha() == s2[:1].isalpha():
            return s1 < s2

        return s1[:1].isalpha()


class URLAttachment(BaseModel):
    attachment_type: Literal["url"] = "url"
    url: str
    content: str


class FileAttachment(BaseModel):
    attachment_type: Literal["file"] = "file"
    file: RemoteFile
    content: str
    truncated: bool = False


class TableSchemaAttachment(BaseModel):
    attachment_type: Literal["table_schema"] = "table_schema"
    table_name: str
    table_schema: dict[str, Any]


class PromptAttachment(BaseModel):
    attachment_type: Literal["prompt"] = "prompt"
    prompt_name: str
    prompt_content: str


MessageAttachment = Annotated[
    FileAttachment | URLAttachment | TableSchemaAttachment | PromptAttachment,
    Field(discriminator="attachment_type"),
]


Direction = Literal[
    "request",
    "response",
]

Namespace = Literal[
    "code_execution",
    "streaming_code_execution",
    "streaming_code_execution_chunk",
    "file_write",
    "command",
    "list_files",
    "error",
    "create_checkpoint",
    "rollback_to_checkpoint",
]

ErrorType = Literal["unknown_request_type", "request_error"]

SupportedLanguage = Literal[
    "python",
    "shell",
]

SUPPORTED_LANGUAGES: list[SupportedLanguage] = ["python", "shell"]


class RemoteExecutionMessageData(BaseModel):
    namespace: Namespace
    direction: Direction
    message_data: str

    def message_type(self) -> str:
        return f"{self.namespace}.{self.direction}"


class RemoteExecutionMessage(BaseModel):
    direction: ClassVar[Direction]
    namespace: ClassVar[Namespace]
    correlation_id: str

    @classmethod
    def message_type(cls) -> str:
        return f"{cls.namespace}.{cls.direction}"

    @property
    def result_key(self) -> str:
        return f"{self.namespace}:{self.correlation_id}"


### Response Types


class RemoteExecutionResponseData(RemoteExecutionMessageData):
    pass


class RemoteExecutionResponse(RemoteExecutionMessage):
    direction: ClassVar[Direction] = "response"


ResponseT = TypeVar("ResponseT", bound=RemoteExecutionResponse)


class StreamingCodeExecutionResponseChunk(RemoteExecutionResponse):
    namespace: ClassVar[Namespace] = "streaming_code_execution_chunk"

    content: str
    truncated: bool = False

    def add(
        self, new_chunk: "StreamingCodeExecutionResponseChunk"
    ) -> "StreamingCodeExecutionResponseChunk":
        """Aggregates content of this and a new chunk."""
        assert self.correlation_id == new_chunk.correlation_id
        return StreamingCodeExecutionResponseChunk(
            correlation_id=self.correlation_id, content=self.content + new_chunk.content
        )


class StreamingCodeExecutionResponse(RemoteExecutionResponse):
    namespace: ClassVar[Namespace] = "streaming_code_execution"

    content: str
    truncated: bool = False

    # Only present for shell code execution
    cancelled_for_timeout: bool = False
    exit_code: int | None = None
    halted: bool = False


class CodeExecutionResponse(RemoteExecutionResponse):
    namespace: ClassVar[Namespace] = "code_execution"

    content: str

    # Only present for shell code execution
    cancelled_for_timeout: bool = False
    exit_code: int | None = None
    halted: bool = False
    truncated: bool = False


class FileWriteResponse(RemoteExecutionResponse):
    namespace: ClassVar[Namespace] = "file_write"

    content: str


class ListFilesResponse(RemoteExecutionResponse):
    namespace: ClassVar[Namespace] = "list_files"

    files: list[RemoteFile]


class ErrorResponse(RemoteExecutionResponse):
    namespace: ClassVar[Namespace] = "error"
    # The namespace of the request that caused the error.
    # Not a Namespace to avoid deserialization errors
    request_namespace: str
    error_type: ErrorType
    error_info: SerializableErrorInfo | None = None

    @property
    def result_key(self) -> str:
        # Match the key of the request that caused the error
        return f"{self.request_namespace}:{self.correlation_id}"


class GitFileChange(BaseModel):
    path: str
    lines_added: int
    lines_deleted: int


class GitDiff(BaseModel):
    files: list[GitFileChange]
    truncated: bool = False  # True if there were more files than the limit
    total_files: int  # Total number of files changed, even if truncated


class GitCommitMetadata(BaseModel):
    author_name: str
    author_email: str
    author_date: str
    commit_date: str
    commit_message: str
    branch: str


class CreateCheckpointResponse(RemoteExecutionResponse):
    namespace: ClassVar[Namespace] = "create_checkpoint"

    correlation_id: str
    head_commit_hash: str
    head_commit_metadata: GitCommitMetadata
    uncommitted_changes_commit_hash: str | None = None
    diff_versus_last_checkpoint: GitDiff | None = None

    debug_info: dict[str, Any] | None = None


class RollbackToCheckpointResponse(RemoteExecutionResponse):
    namespace: ClassVar[Namespace] = "rollback_to_checkpoint"

    debug_info: dict[str, Any] | None = None


### Request Types


class RemoteExecutionRequestData(RemoteExecutionMessageData):
    pass


class RemoteExecutionRequest(RemoteExecutionMessage, Generic[ResponseT]):
    direction: ClassVar[Direction] = "request"


class CodeExecutionRequest(RemoteExecutionRequest[CodeExecutionResponse]):
    namespace: ClassVar[Namespace] = "code_execution"

    language: SupportedLanguage
    content: str
    timeout: int


class StreamingCodeExecutionRequest(
    RemoteExecutionRequest[
        StreamingCodeExecutionResponseChunk | StreamingCodeExecutionResponse
    ]
):
    namespace: ClassVar[Namespace] = "streaming_code_execution"

    language: SupportedLanguage
    content: str
    timeout: int


class FileWriteRequest(RemoteExecutionRequest[FileWriteResponse]):
    namespace: ClassVar[Namespace] = "file_write"

    file_path: str
    # Note we don't use SupportedLanguage here because we don't
    # require language-specific execution support for file writes
    language: str
    write_strategy: FileWriteStrategyName
    content: str


class ListFilesRequest(RemoteExecutionRequest[ListFilesResponse]):
    namespace: ClassVar[Namespace] = "list_files"

    directory: str


class CreateCheckpointRequest(RemoteExecutionRequest[CreateCheckpointResponse]):
    namespace: ClassVar[Namespace] = "create_checkpoint"

    last_checkpoint_head_commit: str | None = None
    last_checkpoint_uncommitted_changes_commit: str | None = None


class RollbackToCheckpointRequest(RemoteExecutionRequest[RollbackToCheckpointResponse]):
    namespace: ClassVar[Namespace] = "rollback_to_checkpoint"

    head_commit: str
    uncommitted_changes_commit: str | None


### Commands


### Command Response Types


class CommandResponse(RemoteExecutionResponse):
    namespace: ClassVar[Namespace] = "command"

    content: str
    content_json: dict[str, Any] = Field(default_factory=dict)
    subcommand: str = "unknown"
    truncated: bool = False


### Command Request Types


class CommandRequest(RemoteExecutionRequest[CommandResponse]):
    namespace: ClassVar[Namespace] = "command"

    data: CommandDataType = Field(..., discriminator="type")


RemoteExecutionRequestType = (
    CodeExecutionRequest
    | FileWriteRequest
    | ListFilesRequest
    | CommandRequest
    | StreamingCodeExecutionRequest
    | CreateCheckpointRequest
    | RollbackToCheckpointRequest
)

RemoteExecutionResponseType = (
    CodeExecutionResponse
    | StreamingCodeExecutionResponseChunk
    | StreamingCodeExecutionResponse
    | FileWriteResponse
    | ListFilesResponse
    | CommandResponse
    | ErrorResponse
    | CreateCheckpointResponse
    | RollbackToCheckpointResponse
)

StreamingResponseType = (
    StreamingCodeExecutionResponseChunk | StreamingCodeExecutionResponse | ErrorResponse
)

STREAMING_NAMESPACES = [
    "streaming_code_execution",
    "streaming_code_execution_chunk",
]


class ChatMode(str, Enum):
    DEFAULT = "DEFAULT"  # chat just with model
    CLI = "CLI"
    CLOUD = "CLOUD"  # chat with cloud devbox
    CODEBASE = "CODEBASE"  # chat with codebase
    PYTHON_INTERPRETER = "PYTHON_INTERPRETER"
    DATABASE = "DATABASE"  # chat with database connection
    WORKFLOW = "WORKFLOW"


DEVBOX_CHAT_MODES = [
    ChatMode.CLOUD,
    ChatMode.CODEBASE,
]


class ChatSource(str, Enum):
    CLI_SHELL = "CLI_SHELL"
    CLI_RUN = "CLI_RUN"
    WEB = "WEB"
    DESKTOP_APP = "DESKTOP_APP"
    VSCODE_EXTENSION = "VSCODE_EXTENSION"


class CLIConnectedState(BaseModel):
    chat_uuid: str
    connected: bool
    last_connected_at: datetime.datetime | None
    connection_latency_ms: int | None
    system_info: SystemInfo | None
    exponent_version: str | None = None
    editable_installation: bool = False


class DevboxConnectedState(str, Enum):
    # TODO: Only needed if we create devbox async
    INITIALIZED = "INITIALIZED"
    # The chat has been initialized, but the devbox is still loading
    DEVBOX_LOADING = "DEVBOX_LOADING"
    # Devbox is ready to use but not tied to a chat
    DEVBOX_READY = "DEVBOX_READY"
    # CLI is connected and running on devbox
    CONNECTED = "CONNECTED"
    # CLI has disconnected
    # TODO: what condition?
    CLI_DISCONNECTED = "CLI_DISCONNECTED"
    # CLI has an error, devbox is running
    CLI_ERROR = "CLI_ERROR"
    # Devbox has an error
    DEVBOX_ERROR = "DEVBOX_ERROR"
    # Devbox is going to idle
    GOING_TO_IDLE = "GOING_TO_IDLE"
    # Devbox is idle
    IDLE = "IDLE"
    # Devbox is going to idle
    RESUMING_FROM_IDLE = "RESUMING_FROM_IDLE"
    # Devbox_shutdown
    # TODO: In theory our terminal state, do we want to name something different?
    DEVBOX_SHUTDOWN = "DEVBOX_SHUTDOWN"


class CloudConnectedState(BaseModel):
    chat_uuid: str
    connected_state: DevboxConnectedState
    last_connected_at: datetime.datetime | None
    system_info: SystemInfo | None


class CLIErrorLog(BaseModel):
    event_data: str
    timestamp: datetime.datetime = datetime.datetime.now()
    attachment_data: str | None = None
    version: str | None = None
    chat_uuid: str | None = None

    @property
    def loaded_event_data(self) -> Any | None:
        try:
            return json.loads(self.event_data)
        except json.JSONDecodeError:
            return None

    @property
    def attachment_bytes(self) -> bytes | None:
        if not self.attachment_data:
            return None
        return self.attachment_data.encode()
