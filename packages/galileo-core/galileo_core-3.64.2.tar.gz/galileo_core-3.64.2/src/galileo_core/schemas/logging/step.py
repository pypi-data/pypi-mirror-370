from datetime import datetime, timezone
from enum import Enum
from json import dumps
from typing import Any, Dict, List, Optional, Sequence, Union

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator
from pydantic.types import UUID4
from pydantic_core.core_schema import ValidationInfo

from galileo_core.schemas.logging.llm import Message
from galileo_core.schemas.shared.document import Document
from galileo_core.utils.json import PydanticJsonEncoder

StepAllowedInputType = Union[str, Sequence[Message]]
StepAllowedOutputType = Union[str, Message, Sequence[Document]]


class StepType(str, Enum):
    llm = "llm"
    retriever = "retriever"
    tool = "tool"
    workflow = "workflow"
    agent = "agent"
    trace = "trace"
    session = "session"


SPAN_TYPES = [StepType.llm, StepType.retriever, StepType.tool, StepType.workflow, StepType.agent]

SPAN_TYPES_WITH_CHILD_SPANS = [StepType.workflow, StepType.agent, StepType.retriever, StepType.tool]

STEP_TYPES_WITH_CHILD_SPANS = [StepType.trace, StepType.workflow, StepType.agent, StepType.retriever, StepType.tool]


class Metrics(BaseModel):
    duration_ns: Optional[int] = Field(
        default=None, description="Duration of the trace or span in nanoseconds.  Displayed as 'Latency' in Galileo."
    )

    model_config = ConfigDict(extra="allow")


class BaseStep(BaseModel):
    type: StepType = Field(description="Type of the trace, span or session.")
    input: Optional[StepAllowedInputType] = Field(
        default=None, description="Input to the trace or span.", union_mode="left_to_right"
    )
    redacted_input: Optional[StepAllowedInputType] = Field(
        default=None, description="Redacted input of the trace or span.", union_mode="left_to_right"
    )
    output: Optional[StepAllowedOutputType] = Field(
        default=None, description="Output of the trace or span.", union_mode="left_to_right"
    )
    redacted_output: Optional[StepAllowedOutputType] = Field(
        default=None, description="Redacted output of the trace or span.", union_mode="left_to_right"
    )
    name: str = Field(default="", description="Name of the trace, span or session.", validate_default=True)
    created_at: datetime = Field(
        title="Created",
        default_factory=lambda: datetime.now(tz=timezone.utc),
        description="Timestamp of the trace or span's creation.",
    )
    user_metadata: Dict[str, str] = Field(
        default_factory=dict, description="Metadata associated with this trace or span."
    )
    tags: List[str] = Field(default_factory=list, description="Tags associated with this trace or span.")
    status_code: Optional[int] = Field(
        default=None, description="Status code of the trace or span. Used for logging failure or error states."
    )
    metrics: Metrics = Field(default_factory=Metrics, description="Metrics associated with this trace or span.")
    external_id: Optional[str] = Field(default=None, description="A user-provided session, trace or span ID.")
    dataset_input: Optional[str] = Field(
        default=None, title="Dataset Input", description="Input to the dataset associated with this trace"
    )
    dataset_output: Optional[str] = Field(
        default=None, title="Dataset Output", description="Output from the dataset associated with this trace"
    )
    dataset_metadata: Dict[str, str] = Field(
        default_factory=dict,
        title="Dataset Metadata",
        description="Metadata from the dataset associated with this trace",
    )
    id: Optional[UUID4] = Field(title="ID", default=None, description="Galileo ID of the session, trace or span")
    session_id: Optional[UUID4] = Field(
        default=None,
        title="Session ID",
        description="Galileo ID of the session containing the trace or span or session",
    )
    trace_id: Optional[UUID4] = Field(
        default=None,
        title="Trace ID",
        description="Galileo ID of the trace containing the span (or the same value as id for a trace)",
    )

    model_config = ConfigDict(validate_assignment=True)

    def __init__(self, **data: Any):
        for k, v in list(data.items()):
            if v is None:
                del data[k]
        super().__init__(**data)

    @field_validator("name", mode="before")
    def set_name(cls, value: Optional[str], info: ValidationInfo) -> str:
        if value is not None:
            return value
        if "type" in info.data:
            return info.data["type"]
        raise ValidationError("could not set step name from type since type is missing")

    @field_validator("input", mode="after")
    def validate_input_serializable(cls, val: StepAllowedInputType) -> StepAllowedInputType:
        # Make sure we can dump input/output to json string.
        dumps(val, cls=PydanticJsonEncoder)
        return val

    @field_validator("output", mode="after")
    def validate_output_serializable(cls, val: StepAllowedOutputType) -> StepAllowedOutputType:
        # Make sure we can dump input/output to json string.
        dumps(val, cls=PydanticJsonEncoder)
        return val
