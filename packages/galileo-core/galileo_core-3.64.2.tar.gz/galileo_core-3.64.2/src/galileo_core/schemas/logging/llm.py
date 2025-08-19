from enum import Enum
from typing import Any, Dict, Generator, List, Optional

from pydantic import BaseModel, RootModel, model_validator


class MessageRole(str, Enum):
    agent = "agent"
    assistant = "assistant"
    developer = "developer"
    function = "function"
    system = "system"
    tool = "tool"
    user = "user"


class Message(BaseModel):
    content: str
    role: MessageRole
    tool_call_id: Optional[str] = None
    tool_calls: Optional[List["ToolCall"]] = None

    @model_validator(mode="before")
    def _allow_null_content_with_tool_calling(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        # Some APIs (like OpenAI) often set content to None when there are tool calls.
        # This is a workaround to allow for that case without changing the type of the field.
        # TODO: Consider making the content field nullable.
        if data.get("content") is None:
            if data.get("tool_calls") is None:
                raise ValueError("at most one of 'content' and 'tool_calls' can be None, but both were None")
            # Deep copy and preserve key order
            data = {k: "" if k == "content" else v for k, v in data.items()}
        return data


class Messages(RootModel[List[Message]]):
    def __len__(self) -> int:
        return len(self.root)

    def __iter__(self) -> Generator[Message, None, None]:  # type: ignore[override]
        yield from self.root

    def __getitem__(self, item: int) -> Message:
        return self.root[item]


class ToolCall(BaseModel):
    id: str
    function: "ToolCallFunction"


class ToolCallFunction(BaseModel):
    name: str
    arguments: str
