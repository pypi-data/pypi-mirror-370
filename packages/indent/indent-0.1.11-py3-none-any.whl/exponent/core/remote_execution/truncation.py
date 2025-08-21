"""Generalized truncation framework for tool results."""

from abc import ABC, abstractmethod
from typing import Any, TypeVar, cast

from msgspec.structs import replace

from exponent.core.remote_execution.cli_rpc_types import (
    BashToolResult,
    ErrorToolResult,
    GlobToolResult,
    GrepToolResult,
    ListToolResult,
    ReadToolResult,
    ToolResult,
    WriteToolResult,
)
from exponent.core.remote_execution.utils import truncate_output

DEFAULT_CHARACTER_LIMIT = 90_000
DEFAULT_LIST_ITEM_LIMIT = 1000
DEFAULT_LIST_PREVIEW_ITEMS = 10


class TruncationStrategy(ABC):
    @abstractmethod
    def should_truncate(self, result: ToolResult) -> bool:
        pass

    @abstractmethod
    def truncate(self, result: ToolResult) -> ToolResult:
        pass


class StringFieldTruncation(TruncationStrategy):
    def __init__(
        self,
        field_name: str,
        character_limit: int = DEFAULT_CHARACTER_LIMIT,
    ):
        self.field_name = field_name
        self.character_limit = character_limit

    def should_truncate(self, result: ToolResult) -> bool:
        if hasattr(result, self.field_name):
            value = getattr(result, self.field_name)
            if isinstance(value, str):
                return len(value) > self.character_limit
        return False

    def truncate(self, result: ToolResult) -> ToolResult:
        if not hasattr(result, self.field_name):
            return result

        value = getattr(result, self.field_name)
        if not isinstance(value, str):
            return result

        truncated_value, was_truncated = truncate_output(value, self.character_limit)

        updates: dict[str, Any] = {self.field_name: truncated_value}
        if hasattr(result, "truncated") and was_truncated:
            updates["truncated"] = True

        return replace(result, **updates)


class ListFieldTruncation(TruncationStrategy):
    def __init__(
        self,
        field_name: str,
        item_limit: int = DEFAULT_LIST_ITEM_LIMIT,
        preview_items: int = DEFAULT_LIST_PREVIEW_ITEMS,
    ):
        self.field_name = field_name
        self.item_limit = item_limit
        self.preview_items = preview_items

    def should_truncate(self, result: ToolResult) -> bool:
        if hasattr(result, self.field_name):
            value = getattr(result, self.field_name)
            if isinstance(value, list):
                return len(value) > self.item_limit
        return False

    def truncate(self, result: ToolResult) -> ToolResult:
        if not hasattr(result, self.field_name):
            return result

        value = getattr(result, self.field_name)
        if not isinstance(value, list):
            return result

        total_items = len(value)
        if total_items <= self.item_limit:
            return result

        truncated_count = max(0, total_items - 2 * self.preview_items)
        truncated_list = (
            value[: self.preview_items]
            + [f"... {truncated_count} items truncated ..."]
            + value[-self.preview_items :]
        )

        updates: dict[str, Any] = {self.field_name: truncated_list}
        if hasattr(result, "truncated"):
            updates["truncated"] = True

        return replace(result, **updates)


class CompositeTruncation(TruncationStrategy):
    def __init__(self, strategies: list[TruncationStrategy]):
        self.strategies = strategies

    def should_truncate(self, result: ToolResult) -> bool:
        return any(strategy.should_truncate(result) for strategy in self.strategies)

    def truncate(self, result: ToolResult) -> ToolResult:
        for strategy in self.strategies:
            if strategy.should_truncate(result):
                result = strategy.truncate(result)
        return result


class TailTruncation(TruncationStrategy):
    """Truncation strategy that keeps the end of the output (tail) instead of the beginning."""

    def __init__(
        self,
        field_name: str,
        character_limit: int = DEFAULT_CHARACTER_LIMIT,
    ):
        self.field_name = field_name
        self.character_limit = character_limit

    def should_truncate(self, result: ToolResult) -> bool:
        if hasattr(result, self.field_name):
            value = getattr(result, self.field_name)
            if isinstance(value, str):
                return len(value) > self.character_limit
        return False

    def truncate(self, result: ToolResult) -> ToolResult:
        if not hasattr(result, self.field_name):
            return result

        value = getattr(result, self.field_name)
        if not isinstance(value, str):
            return result

        if len(value) <= self.character_limit:
            return result

        # Keep the last character_limit characters
        truncated_value = value[-self.character_limit :]

        # Try to start at a newline if possible for cleaner output
        newline_pos = truncated_value.find("\n")
        if (
            newline_pos != -1 and newline_pos < 1000
        ):  # Only adjust if newline is reasonably close to start
            truncated_value = truncated_value[newline_pos + 1 :]

        # Add truncation indicator at the beginning
        truncation_msg = f"... (output truncated, showing last {len(truncated_value)} characters) ...\n"
        truncated_value = truncation_msg + truncated_value

        updates: dict[str, Any] = {self.field_name: truncated_value}
        if hasattr(result, "truncated"):
            updates["truncated"] = True

        return replace(result, **updates)


class StringListTruncation(TruncationStrategy):
    """Truncation for lists of strings that limits both number of items and individual string length."""

    def __init__(
        self,
        field_name: str,
        max_items: int = DEFAULT_LIST_ITEM_LIMIT,
        preview_items: int = DEFAULT_LIST_PREVIEW_ITEMS,
        max_item_length: int = 1000,
    ):
        self.field_name = field_name
        self.max_items = max_items
        self.preview_items = preview_items
        self.max_item_length = max_item_length

    def should_truncate(self, result: ToolResult) -> bool:
        if not hasattr(result, self.field_name):
            return False

        items = getattr(result, self.field_name)
        if not isinstance(items, list):
            return False

        # Check if we need to truncate number of items
        if len(items) > self.max_items:
            return True

        # Check if any individual item is too long
        for item in items:
            if isinstance(item, str) and len(item) > self.max_item_length:
                return True
            # Handle dict items (e.g., with metadata like file path and line number)
            elif isinstance(item, dict) and "content" in item:
                if len(item["content"]) > self.max_item_length:
                    return True

        return False

    def _truncate_item_content(
        self, item: str | dict[str, Any]
    ) -> str | dict[str, Any]:
        """Truncate an individual item's content."""
        if isinstance(item, str):
            if len(item) <= self.max_item_length:
                return item
            # Truncate string item
            truncated, _ = truncate_output(item, self.max_item_length)
            return truncated
        elif isinstance(item, dict) and "content" in item:
            # Handle dict-style items (e.g., with metadata like file path and line number)
            if len(item["content"]) <= self.max_item_length:
                return item
            truncated_content, _ = truncate_output(
                item["content"], self.max_item_length
            )
            return {**item, "content": truncated_content}
        else:
            return item

    def truncate(self, result: ToolResult) -> ToolResult:
        if not hasattr(result, self.field_name):
            return result

        items = getattr(result, self.field_name)
        if not isinstance(items, list):
            return result

        # First, truncate individual item contents
        truncated_items = [self._truncate_item_content(item) for item in items]

        # Then, limit the number of items if needed
        total_items = len(truncated_items)
        if total_items > self.max_items:
            truncated_count = max(0, total_items - 2 * self.preview_items)
            final_items = (
                truncated_items[: self.preview_items]
                + [f"... {truncated_count} items truncated ..."]
                + truncated_items[-self.preview_items :]
            )
        else:
            final_items = truncated_items

        updates: dict[str, Any] = {self.field_name: final_items}
        if hasattr(result, "truncated"):
            updates["truncated"] = True

        return replace(result, **updates)


TRUNCATION_REGISTRY: dict[type[ToolResult], TruncationStrategy] = {
    ReadToolResult: StringFieldTruncation("content"),
    WriteToolResult: StringFieldTruncation("message"),
    BashToolResult: TailTruncation("shell_output"),
    GrepToolResult: StringListTruncation("matches"),
    GlobToolResult: StringListTruncation("filenames", max_item_length=4096),
    ListToolResult: StringListTruncation("files", max_item_length=4096),
}


T = TypeVar("T", bound=ToolResult)


def truncate_tool_result(result: T) -> T:
    if isinstance(result, ErrorToolResult):
        return cast(T, result)

    result_type = type(result)
    if result_type in TRUNCATION_REGISTRY:
        strategy = TRUNCATION_REGISTRY[result_type]
        if strategy.should_truncate(result):
            return cast(T, strategy.truncate(result))

    return result
