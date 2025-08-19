from collections import deque
from datetime import datetime
from json import dumps
from typing import Deque, Dict, List, Optional

from pydantic import BaseModel, Field
from pydantic.types import UUID4

from galileo_core.schemas.logging.agent import AgentType
from galileo_core.schemas.logging.span import (
    AgentSpan,
    LlmMetrics,
    LlmSpan,
    LlmSpanAllowedInputType,
    LlmSpanAllowedOutputType,
    RetrieverSpan,
    Span,
    StepWithChildSpans,
    ToolSpan,
    WorkflowSpan,
)
from galileo_core.schemas.logging.step import Metrics
from galileo_core.schemas.logging.trace import Trace
from galileo_core.schemas.shared.document import Document
from galileo_core.utils.json import PydanticJsonEncoder


class TracesLogger(BaseModel):
    traces: List[Trace] = Field(default_factory=list, description="List of traces.")
    _parent_stack: Deque[StepWithChildSpans] = deque()

    def current_parent(self) -> Optional[StepWithChildSpans]:
        return self._parent_stack[-1] if self._parent_stack else None

    def add_child_span_to_parent(self, span: Span) -> None:
        current_parent = self.current_parent()
        if current_parent is None:
            raise ValueError("A trace needs to be created in order to add a span.")
        span.dataset_input = current_parent.dataset_input
        span.dataset_output = current_parent.dataset_output
        span.dataset_metadata = current_parent.dataset_metadata
        current_parent.add_child_span(span)

    def add_trace(
        self,
        input: str,
        redacted_input: Optional[str] = None,
        output: Optional[str] = None,
        redacted_output: Optional[str] = None,
        name: Optional[str] = None,
        created_at: Optional[datetime] = None,
        duration_ns: Optional[int] = None,
        user_metadata: Optional[Dict[str, str]] = None,
        tags: Optional[List[str]] = None,
        dataset_input: Optional[str] = None,
        dataset_output: Optional[str] = None,
        dataset_metadata: Optional[Dict[str, str]] = None,
        external_id: Optional[str] = None,
        id: Optional[UUID4] = None,
    ) -> Trace:
        """
        Create a new trace and add it to the list of traces.
        Simple usage:
        ```
        my_traces.add_trace("input")
        my_traces.add_llm_span("input", "output", model="<my_model>")
        my_traces.conclude("output")
        ```
        Parameters:
        ----------
            input: str: Input to the node.
            redacted_input: Optional[str]: Redacted input to the node.
            output: Optional[str]: Output of the node.
            redacted_output: Optional[str]: Redacted output of the node.
            name: Optional[str]: Name of the trace.
            duration_ns: Optional[int]: Duration of the trace in nanoseconds.
            created_at: Optional[datetime]: Timestamp of the trace's creation.
            user_metadata: Optional[Dict[str, str]]: Metadata associated with this trace.
            ground_truth: Optional[str]: Ground truth, expected output of the trace.
        Returns:
        -------
            Trace: The created trace.
        """
        if self.current_parent() is not None:
            raise ValueError("You must conclude the existing trace before adding a new one.")
        trace = Trace(
            input=input,
            redacted_input=redacted_input,
            output=output,
            redacted_output=redacted_output,
            name=name,
            created_at=created_at,
            user_metadata=user_metadata,
            tags=tags,
            metrics=Metrics(duration_ns=duration_ns),
            dataset_input=dataset_input,
            dataset_output=dataset_output,
            dataset_metadata=dataset_metadata if dataset_metadata is not None else {},
            external_id=external_id,
            id=id,
        )
        self.traces.append(trace)
        self._parent_stack.append(trace)
        return trace

    def add_single_llm_span_trace(
        self,
        input: LlmSpanAllowedInputType,
        output: LlmSpanAllowedOutputType,
        model: Optional[str],
        redacted_input: Optional[LlmSpanAllowedInputType] = None,
        redacted_output: Optional[LlmSpanAllowedOutputType] = None,
        tools: Optional[List[Dict]] = None,
        name: Optional[str] = None,
        created_at: Optional[datetime] = None,
        duration_ns: Optional[int] = None,
        user_metadata: Optional[Dict[str, str]] = None,
        tags: Optional[List[str]] = None,
        num_input_tokens: Optional[int] = None,
        num_output_tokens: Optional[int] = None,
        total_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        status_code: Optional[int] = None,
        time_to_first_token_ns: Optional[int] = None,
        dataset_input: Optional[str] = None,
        dataset_output: Optional[str] = None,
        dataset_metadata: Optional[Dict[str, str]] = None,
        trace_id: Optional[UUID4] = None,
        span_id: Optional[UUID4] = None,
        span_step_number: Optional[int] = None,
    ) -> Trace:
        """
        Create a new trace with a single span and add it to the list of traces.

        Parameters:
        ----------
            input: LlmStepAllowedIOType: Input to the node.
            output: LlmStepAllowedIOType: Output of the node.
            model: str: Model used for this span. Feedback from April: Good docs about what model names we use.
            redacted_input: Optional[LlmStepAllowedIOType]: Redacted input to the node.
            redacted_output: Optional[LlmStepAllowedIOType]: Redacted output of the node
            tools: Optional[List[Dict]]: List of available tools passed to LLM on invocation.
            name: Optional[str]: Name of the span.
            duration_ns: Optional[int]: duration_ns of the node in nanoseconds.
            created_at: Optional[datetime]: Timestamp of the span's creation.
            user_metadata: Optional[Dict[str, str]]: Metadata associated with this span.
            num_input_tokens: Optional[int]: Number of input tokens.
            num_output_tokens: Optional[int]: Number of output tokens.
            total_tokens: Optional[int]: Total number of tokens.
            temperature: Optional[float]: Temperature used for generation.
            ground_truth: Optional[str]: Ground truth, expected output of the workflow.
            status_code: Optional[int]: Status code of the node execution.
            time_to_first_token_ns: Optional[int]: Time until the first token was returned.
            dataset_input: Optional[str]: Dataset input for the span.
            dataset_output: Optional[str]: Dataset output for the span.
            dataset_metadata: Optional[Dict[str, str]]: Dataset metadata for the span.
            trace_id: Optional[UUID4]: ID of the trace.
            span_id: Optional[UUID4]: ID of the span.
            span_step_number: Optional[int]: Step number of the span.
        Returns:
        -------
            Trace: The created trace.
        """
        if self.current_parent() is not None:
            raise ValueError("A trace cannot be created within a parent trace or span, it must always be the root.")

        trace = Trace(
            input=dumps(input, cls=PydanticJsonEncoder),
            redacted_input=dumps(redacted_input, cls=PydanticJsonEncoder) if redacted_input else None,
            output=dumps(output, cls=PydanticJsonEncoder),
            redacted_output=dumps(redacted_output, cls=PydanticJsonEncoder) if redacted_output else None,
            name=name,
            created_at=created_at,
            user_metadata=user_metadata,
            tags=tags,
            dataset_input=dataset_input,
            dataset_output=dataset_output,
            dataset_metadata=dataset_metadata if dataset_metadata is not None else {},
            id=trace_id,
        )
        trace.add_child_span(
            LlmSpan(
                name=name,
                created_at=created_at,
                user_metadata=user_metadata,
                tags=tags,
                input=input,
                redacted_input=redacted_input,
                output=output,
                redacted_output=redacted_output,
                metrics=LlmMetrics(
                    duration_ns=duration_ns,
                    num_input_tokens=num_input_tokens,
                    num_output_tokens=num_output_tokens,
                    num_total_tokens=total_tokens,
                    time_to_first_token_ns=time_to_first_token_ns,
                ),
                tools=tools,
                model=model,
                temperature=temperature,
                status_code=status_code,
                dataset_input=dataset_input,
                dataset_output=dataset_output,
                dataset_metadata=dataset_metadata if dataset_metadata is not None else {},
                id=span_id,
                step_number=span_step_number,
            )
        )
        self.traces.append(trace)
        # Single span traces are automatically concluded so we reset the current parent.
        self._parent_stack = deque()
        return trace

    def add_llm_span(
        self,
        input: LlmSpanAllowedInputType,
        output: LlmSpanAllowedOutputType,
        model: Optional[str],
        redacted_input: Optional[LlmSpanAllowedInputType] = None,
        redacted_output: Optional[LlmSpanAllowedOutputType] = None,
        tools: Optional[List[Dict]] = None,
        name: Optional[str] = None,
        created_at: Optional[datetime] = None,
        duration_ns: Optional[int] = None,
        user_metadata: Optional[Dict[str, str]] = None,
        tags: Optional[List[str]] = None,
        num_input_tokens: Optional[int] = None,
        num_output_tokens: Optional[int] = None,
        total_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        status_code: Optional[int] = None,
        time_to_first_token_ns: Optional[int] = None,
        id: Optional[UUID4] = None,
        step_number: Optional[int] = None,
    ) -> LlmSpan:
        """
        Add a new llm span to the current parent.

        Parameters:
        ----------
            input: LlmStepAllowedIOType: Input to the node.
            output: LlmStepAllowedIOType: Output of the node.
            model: str: Model used for this span.
            redacted_input: Optional[LlmStepAllowedIOType]: Redacted input to the node.
            redacted_output: Optional[LlmStepAllowedIOType]: Redacted output of the node
            tools: Optional[List[Dict]]: List of available tools passed to LLM on invocation.
            name: Optional[str]: Name of the span.
            duration_ns: Optional[int]: duration_ns of the node in nanoseconds.
            created_at: Optional[datetime]: Timestamp of the span's creation.
            user_metadata: Optional[Dict[str, str]]: Metadata associated with this span.
            num_input_tokens: Optional[int]: Number of input tokens.
            num_output_tokens: Optional[int]: Number of output tokens.
            total_tokens: Optional[int]: Total number of tokens.
            temperature: Optional[float]: Temperature used for generation.
            status_code: Optional[int]: Status code of the node execution.
            time_to_first_token_ns: Optional[int]: Time until the first token was returned.
            id: Optional[UUID4]: ID of the span.
            step_number: Optional[int]: Step number of the span.
        Returns:
        -------
            LlmSpan: The created span.
        """

        span = LlmSpan(
            input=input,
            redacted_input=redacted_input,
            output=output,
            redacted_output=redacted_output,
            name=name,
            created_at=created_at,
            user_metadata=user_metadata,
            tags=tags,
            metrics=LlmMetrics(
                duration_ns=duration_ns,
                num_input_tokens=num_input_tokens,
                num_output_tokens=num_output_tokens,
                num_total_tokens=total_tokens,
                time_to_first_token_ns=time_to_first_token_ns,
            ),
            tools=tools,
            model=model,
            temperature=temperature,
            status_code=status_code,
            id=id,
            step_number=step_number,
        )
        self.add_child_span_to_parent(span)
        return span

    def add_retriever_span(
        self,
        input: str,
        documents: List[Document],
        redacted_input: Optional[str] = None,
        redacted_documents: Optional[List[Document]] = None,
        name: Optional[str] = None,
        duration_ns: Optional[int] = None,
        created_at: Optional[datetime] = None,
        user_metadata: Optional[Dict[str, str]] = None,
        tags: Optional[List[str]] = None,
        status_code: Optional[int] = None,
        id: Optional[UUID4] = None,
        step_number: Optional[int] = None,
    ) -> RetrieverSpan:
        """
        Add a new retriever span to the current parent.

        Parameters:
        ----------
            input: str: Input to the node.
            documents: List[Document]: Documents retrieved from the retriever.
            redacted_input: Optional[str]: Redacted input to the node.
            redacted_documents: Optional[List[Document]]: Redacted documents retrieved from the retriever.
            name: Optional[str]: Name of the span.
            duration_ns: Optional[int]: duration_ns of the node in nanoseconds.
            created_at: Optional[datetime]: Timestamp of the span's creation.
            user_metadata: Optional[Dict[str, str]]: Metadata associated with this span.
            status_code: Optional[int]: Status code of the node execution.
            id: Optional[UUID4]: ID of the span.
            step_number: Optional[int]: Step number of the span.
        Returns:
        -------
            RetrieverSpan: The created span.
        """
        span = RetrieverSpan(
            input=input,
            redacted_input=redacted_input,
            output=documents,
            redacted_output=redacted_documents,
            name=name,
            created_at=created_at,
            user_metadata=user_metadata,
            tags=tags,
            status_code=status_code,
            metrics=Metrics(duration_ns=duration_ns),
            id=id,
            step_number=step_number,
        )
        self.add_child_span_to_parent(span)
        return span

    def add_tool_span(
        self,
        input: str,
        redacted_input: Optional[str] = None,
        output: Optional[str] = None,
        redacted_output: Optional[str] = None,
        name: Optional[str] = None,
        duration_ns: Optional[int] = None,
        created_at: Optional[datetime] = None,
        user_metadata: Optional[Dict[str, str]] = None,
        tags: Optional[List[str]] = None,
        status_code: Optional[int] = None,
        tool_call_id: Optional[str] = None,
        id: Optional[UUID4] = None,
        step_number: Optional[int] = None,
    ) -> ToolSpan:
        """
        Add a new tool span to the current parent.

        Parameters:
        ----------
            input: str: Input to the node.
            redacted_input: Optional[str]: Redacted input to the node.
            output: Optional[str]: Output of the node.
            redacted_output: Optional[str]: Redacted output of the node.
            name: Optional[str]: Name of the span.
            duration_ns: Optional[int]: duration_ns of the node in nanoseconds.
            created_at: Optional[datetime]: Timestamp of the span's creation.
            user_metadata: Optional[Dict[str, str]]: Metadata associated with this span.
            status_code: Optional[int]: Status code of the node execution.
            tool_call_id: Optional[str]: ID of the tool call.
            id: Optional[UUID4]: ID of the span.
            step_number: Optional[int]: Step number of the span.
        Returns:
        -------
            ToolSpan: The created span.
        """
        span = ToolSpan(
            input=input,
            redacted_input=redacted_input,
            output=output,
            redacted_output=redacted_output,
            name=name,
            created_at=created_at,
            user_metadata=user_metadata,
            tags=tags,
            status_code=status_code,
            tool_call_id=tool_call_id,
            metrics=Metrics(duration_ns=duration_ns),
            id=id,
            step_number=step_number,
        )
        self.add_child_span_to_parent(span)
        return span

    def add_workflow_span(
        self,
        input: str,
        redacted_input: Optional[str] = None,
        output: Optional[str] = None,
        redacted_output: Optional[str] = None,
        name: Optional[str] = None,
        duration_ns: Optional[int] = None,
        created_at: Optional[datetime] = None,
        user_metadata: Optional[Dict[str, str]] = None,
        tags: Optional[List[str]] = None,
        id: Optional[UUID4] = None,
        step_number: Optional[int] = None,
    ) -> WorkflowSpan:
        """
        Add a workflow span to the current parent. This is useful when you want to create a nested workflow span
        within the trace or current workflow span. The next span you add will be a child of the current parent. To
        move out of the nested workflow, use conclude().

        Parameters:
        ----------
            input: str: Input to the node.
            redacted_input: Optional[str]: Redacted input to the node.
            output: Optional[str]: Output of the node. This can also be set on conclude().
            redacted_output: Optional[str]: Redacted output of the node.
            name: Optional[str]: Name of the span.
            duration_ns: Optional[int]: duration_ns of the node in nanoseconds.
            created_at: Optional[datetime]: Timestamp of the span's creation.
            user_metadata: Optional[Dict[str, str]]: Metadata associated with this span.
            id: Optional[UUID4]: ID of the span.
            step_number: Optional[int]: Step number of the span.
        Returns:
        -------
            WorkflowSpan: The created span.
        """
        span = WorkflowSpan(
            input=input,
            redacted_input=redacted_input,
            output=output,
            redacted_output=redacted_output,
            name=name,
            created_at=created_at,
            user_metadata=user_metadata,
            tags=tags,
            metrics=Metrics(duration_ns=duration_ns),
            id=id,
            step_number=step_number,
        )
        self.add_child_span_to_parent(span)
        self._parent_stack.append(span)
        return span

    def add_agent_span(
        self,
        input: str,
        redacted_input: Optional[str] = None,
        output: Optional[str] = None,
        redacted_output: Optional[str] = None,
        name: Optional[str] = None,
        duration_ns: Optional[int] = None,
        created_at: Optional[datetime] = None,
        user_metadata: Optional[Dict[str, str]] = None,
        tags: Optional[List[str]] = None,
        agent_type: Optional[AgentType] = None,
        id: Optional[UUID4] = None,
        step_number: Optional[int] = None,
    ) -> AgentSpan:
        """
        Parameters:
        ----------
            input: str: Input to the node.
            redacted_input: Optional[str]: Redacted input to the node.
            output: Optional[str]: Output of the node. This can also be set on conclude().
            redacted_output: Optional[str]: Redacted output of the node.
            name: Optional[str]: Name of the span.
            duration_ns: Optional[int]: duration_ns of the node in nanoseconds.
            created_at: Optional[datetime]: Timestamp of the span's creation.
            user_metadata: Optional[Dict[str, str]]: Metadata associated with this span.
            agent_type: Optional[AgentType]: Agent type of the span.
            step_number: Optional[int]: Step number of the span.
        Returns
        -------
            AgentSpan: The created span.
        """
        span = AgentSpan(
            input=input,
            redacted_input=redacted_input,
            output=output,
            redacted_output=redacted_output,
            name=name,
            created_at=created_at,
            user_metadata=user_metadata,
            tags=tags,
            metrics=Metrics(duration_ns=duration_ns),
            agent_type=agent_type,
            id=id,
            step_number=step_number,
        )
        self.add_child_span_to_parent(span)
        self._parent_stack.append(span)
        return span

    def conclude(
        self,
        output: Optional[str] = None,
        redacted_output: Optional[str] = None,
        duration_ns: Optional[int] = None,
        status_code: Optional[int] = None,
    ) -> Optional[StepWithChildSpans]:
        """
        Conclude the current trace or workflow span by setting the output of the current node. In the case of nested
        workflow spans, this will point the workflow back to the parent of the current workflow span.

        Parameters:
        ----------
            output: Optional[str]: Output of the node.
            redacted_output: Optional[str]: Redacted output of the node.
            duration_ns: Optional[int]: duration_ns of the node in nanoseconds.
            status_code: Optional[int]: Status code of the node execution.
        Returns:
        -------
            Optional[StepWithChildSpans]: The parent of the current workflow. None if no parent exists.
        """
        current_parent = self.current_parent()
        if current_parent is None:
            raise ValueError("No existing workflow to conclude.")

        current_parent.output = output or current_parent.output
        if redacted_output is not None:
            current_parent.redacted_output = redacted_output or current_parent.redacted_output
        current_parent.status_code = status_code
        if duration_ns is not None:
            current_parent.metrics.duration_ns = duration_ns

        finished_step = self._parent_stack.pop()
        if self.current_parent() is None and not isinstance(finished_step, Trace):
            raise ValueError("Finished step is not a trace, but has no parent.  Not added to the list of traces.")
        return self.current_parent()
