import logging
import uuid
from collections.abc import Iterator, Sequence
from functools import lru_cache
from typing import Any

import grpc
from google.protobuf.struct_pb2 import Struct  # type: ignore[import-untyped]
from langchain_core.messages import BaseMessage, BaseMessageChunk
from langgraph.checkpoint.base import Checkpoint
from langgraph.errors import GraphBubbleUp, GraphInterrupt
from langgraph.pregel import Pregel
from langgraph.pregel._algo import apply_writes
from langgraph.pregel._checkpoint import channels_from_checkpoint
from langgraph.pregel._retry import run_with_retry

from langgraph_executor.common import (
    checkpoint_to_proto,
    exception_to_pb,
    extract_channels,
    get_graph,
    pb_to_val,
    reconstruct_channels,
    reconstruct_checkpoint,
    reconstruct_task_writes,
    updates_to_proto,
)
from langgraph_executor.execute_task import (
    extract_writes,
    get_init_request,
    reconstruct_task,
)
from langgraph_executor.extract_graph import extract_graph
from langgraph_executor.pb import executor_pb2, executor_pb2_grpc, types_pb2
from langgraph_executor.stream_utils import ExecutorStreamHandler


class LangGraphExecutorServicer(executor_pb2_grpc.LangGraphExecutorServicer):
    """gRPC servicer for LangGraph runtime execution operations."""

    def __init__(self, graphs: dict[str, Pregel]):
        """Initialize the servicer with compiled graphs.

        Args:
            graphs: Dictionary mapping graph names to compiled graphs

        """
        self.graphs = graphs
        self.logger = logging.getLogger(__name__)

    def ListGraphs(self, request: Any, context: Any) -> executor_pb2.ListGraphsResponse:  # type: ignore[name-defined]
        """List available graphs."""
        return executor_pb2.ListGraphsResponse(
            graph_names=list(self.graphs.keys()),
        )

    def GetGraph(self, request: Any, context: Any) -> executor_pb2.GetGraphResponse:  # type: ignore[name-defined]
        """Get graph definition."""
        try:
            self.logger.debug("GetGraph called")

            graph = self.graphs[request.graph_name]

            # extract graph
            graph_definition = extract_graph(graph)

            return executor_pb2.GetGraphResponse(graph_definition=graph_definition)

        except Exception as e:
            self.logger.error(f"GetGraph Error: {e}", exc_info=True)
            context.abort(grpc.StatusCode.INTERNAL, str(e))

    def ChannelsFromCheckpoint(
        self, request: Any, context: Any
    ) -> executor_pb2.ChannelsFromCheckpointResponse:  # type: ignore[name-defined]
        try:
            self.logger.debug("ChannelsFromCheckpoint called")

            graph = get_graph(request.graph_name, self.graphs)

            # reconstruct specs
            specs, _ = reconstruct_channels(
                request.specs.channels,
                graph,
                scratchpad=None,  # type: ignore[invalid-arg-type]
            )

            # initialize channels from specs and checkpoint channel values
            checkpoint_dummy = Checkpoint(  # type: ignore[typeddict-item]
                channel_values={
                    k: pb_to_val(v)
                    for k, v in request.checkpoint_channel_values.items()
                },
            )
            channels, _ = channels_from_checkpoint(specs, checkpoint_dummy)

            # channels to pb
            channels = extract_channels(channels)

            return executor_pb2.ChannelsFromCheckpointResponse(channels=channels)

        except Exception as e:
            self.logger.error(f"ChannelsFromCheckpoint Error: {e}", exc_info=True)
            context.abort(grpc.StatusCode.INTERNAL, str(e))

    def ExecuteTask(
        self,
        request_iterator: Iterator[executor_pb2.ExecuteTaskRequest],  # type: ignore[name-defined]
        context: Any,
    ) -> Iterator[executor_pb2.ExecuteTaskResponse]:  # type: ignore[name-defined]
        self.logger.debug("ExecuteTask called")
        _patch_specific_base_message()

        # Right now, only handle task execution without interrupts, etc
        try:
            request = get_init_request(request_iterator)

            # Reconstruct PregelExecutableTask
            graph = get_graph(request.graph_name, self.graphs)
            stream_messages = "messages" in request.stream_modes
            stream_custom = "custom" in request.stream_modes

            stream_chunks = []

            custom_stream_writer = (
                self._create_custom_stream_writer(stream_chunks)
                if stream_custom
                else None
            )

            task = reconstruct_task(
                request, graph, custom_stream_writer=custom_stream_writer
            )
            if stream_messages:

                def stream_callback(message: BaseMessageChunk, metadata: dict):
                    """Callback to capture stream chunks and queue them."""
                    try:
                        stream_chunks.append(
                            executor_pb2.ExecuteTaskResponse(
                                message_or_message_chunk=extract_output_message(message)
                            )
                        )
                    except Exception as e:
                        self.logger.warning(
                            f"Failed to create stream chunk: {e}", exc_info=True
                        )

                # Create and inject callback handler
                stream_handler = ExecutorStreamHandler(stream_callback, task.id)

                # Add handler to task config callbacks
                if "callbacks" not in task.config:
                    task.config["callbacks"] = []
                task.config["callbacks"].append(stream_handler)  # type: ignore[union-attr]

            # Execute task, catching interrupts
            # Check cache if task has cache key - send request to Go orchestrator
            should_execute = True
            if task.cache_key:
                self.logger.debug(
                    f"Task {task.id} has cache key, sending cache check request to Go",
                )

                # Send cache check request to Go runtime
                cache_check_request = executor_pb2.CacheCheckRequest(
                    cache_namespace=list(task.cache_key.ns),
                    cache_key=task.cache_key.key,
                    ttl=task.cache_key.ttl,
                )

                yield executor_pb2.ExecuteTaskResponse(
                    cache_check_request=cache_check_request,
                )

                # Wait for Go's response via the bidirectional stream
                try:
                    cache_response_request = next(request_iterator)
                    if hasattr(cache_response_request, "cache_check_response"):
                        cache_response = cache_response_request.cache_check_response
                        should_execute = not cache_response.cache_hit
                        self.logger.debug(
                            f"Received cache response for task {task.id}: cache_hit={cache_response.cache_hit}",
                        )
                    else:
                        self.logger.warning(
                            f"Expected cache_check_response for task {task.id}, got unexpected message type",
                        )
                        should_execute = (
                            True  # Default to execution if unexpected response
                        )
                except StopIteration:
                    self.logger.warning(
                        f"No cache response received for task {task.id}, defaulting to execution",
                    )
                    should_execute = True  # Default to execution if no response

            # TODO patch retry policy
            # TODO configurable to deal with _call and the functional api

            exception_pb = None
            if not should_execute:
                # Skip execution but still send response
                pass
            try:
                run_with_retry(
                    task,
                    retry_policy=None,
                )
                # Yield any accumulated stream chunks
                yield from stream_chunks

            except Exception as e:
                if isinstance(e, GraphBubbleUp | GraphInterrupt):
                    self.logger.info(f"Interrupt in task {task.id}: {e}")
                else:
                    self.logger.exception(
                        f"Exception running task {task.id}: {e}\nTask: {task}\n\n",
                        exc_info=True,
                    )
                exception_pb = exception_to_pb(e)

            # Send final messages via message_chunk if they exist
            final_messages = extract_output_messages(task.writes)
            if final_messages:
                for message in final_messages:
                    yield executor_pb2.ExecuteTaskResponse(
                        message_or_message_chunk=message
                    )

            # Extract and yield channel writes
            writes_pb = extract_writes(task.writes)
            task_result_pb = (
                executor_pb2.TaskResult(error=exception_pb, writes=writes_pb)
                if exception_pb
                else executor_pb2.TaskResult(writes=writes_pb)
            )

            yield executor_pb2.ExecuteTaskResponse(task_result=task_result_pb)

            # Generate streaming chunks
            # for chunk in output_writes(task, request):
            #     yield executor_pb2.ExecuteTaskResponse(stream_chunk=chunk)

        except Exception as e:
            self.logger.exception(f"ExecuteTask error: {e}")
            context.abort(grpc.StatusCode.INTERNAL, str(e))

    def ApplyWrites(
        self, request: Any, context: Any
    ) -> executor_pb2.ApplyWritesResponse:  # type: ignore[name-defined]
        # get graph
        self.logger.debug("ApplyWrites called")
        try:
            # Reconstruct python objects from proto
            graph = get_graph(request.graph_name, self.graphs)
            channels, _ = reconstruct_channels(
                request.channels.channels,
                graph,
                # TODO: figure this out
                scratchpad=None,  # type: ignore[invalid-arg-type]
            )
            checkpoint = reconstruct_checkpoint(request.checkpoint)
            tasks = reconstruct_task_writes(request.tasks)

            # apply writes
            updated_channel_names_set = apply_writes(
                checkpoint,
                channels,
                tasks,
                lambda *args: request.next_version,
                graph.trigger_to_nodes,
            )
            updated_channel_names = list(updated_channel_names_set)

            # Reconstruct protos
            updated_channels = extract_channels(channels)
            checkpoint_proto = checkpoint_to_proto(checkpoint)

            # Respond with updates
            return executor_pb2.ApplyWritesResponse(
                updates=updates_to_proto(
                    checkpoint_proto,
                    updated_channel_names,
                    updated_channels,
                ),
            )

        except Exception as e:
            self.logger.exception(f"ApplyWrites error: {e}")
            context.abort(grpc.StatusCode.INTERNAL, str(e))

    def _create_custom_stream_writer(self, stream_chunks):
        """Create a proper stream_writer function for custom mode (like langgraph does)."""
        from google.protobuf.struct_pb2 import Struct  # type: ignore[unresolved-import]

        def stream_writer(content):
            """Custom stream writer that creates CustomStreamEvent messages."""
            try:
                # Create payload struct (like langgraph does)
                payload = Struct()
                if isinstance(content, str):
                    payload.update({"content": content})
                elif isinstance(content, dict):
                    payload.update(content)
                else:
                    payload.update({"content": str(content)})

                # Create CustomStreamEvent
                custom_event = executor_pb2.CustomStreamEvent(payload=payload)
                custom_event_response = executor_pb2.ExecuteTaskResponse(
                    custom_stream_event=custom_event
                )
                stream_chunks.append(custom_event_response)

            except Exception as e:
                self.logger.warning(
                    f"Failed to create custom stream event: {e}", exc_info=True
                )

        return stream_writer


def extract_output_messages(writes: Sequence[Any]) -> list[types_pb2.Message]:  # type: ignore[name-defined]
    messages = []
    for write in writes:
        # Not sure this check is right
        if isinstance(write[1], BaseMessage):
            messages.append(extract_output_message(write[1]))
        elif isinstance(write[1], Sequence):
            messages.extend(
                [
                    extract_output_message(w)
                    for w in write[1]
                    if isinstance(w, BaseMessage)
                ]
            )

    return messages


def extract_output_message(write: Any) -> types_pb2.Message:  # type: ignore[name-defined]
    message = Struct()
    message.update(
        {
            "is_streaming_chunk": False,
            "message": {
                "id": getattr(write, "id", None) or uuid.uuid4().hex,
                "type": getattr(write, "type", None),
                "content": str(getattr(write, "content", "") or ""),
                "additional_kwargs": getattr(write, "additional_kwargs", {}),
                "usage_metadata": getattr(write, "usage_metadata", {}),
                "tool_calls": getattr(write, "tool_calls", []),
                "tool_call_id": getattr(write, "tool_call_id", ""),
                "tool_call_chunks": getattr(write, "tool_call_chunks", []),
                "response_metadata": getattr(write, "response_metadata", {}),
            },
            "metadata": {},
        }
    )
    return types_pb2.Message(payload=message)


@lru_cache(maxsize=1)
def _patch_specific_base_message() -> None:
    """Patch the specific BaseMessage class used in your system."""
    from langchain_core.messages import BaseMessage

    original_init = BaseMessage.__init__

    def patched_init(self, content: Any, **kwargs: Any) -> None:
        original_init(self, content, **kwargs)
        if self.id is None:
            self.id = str(uuid.uuid4())

    BaseMessage.__init__ = patched_init  # type: ignore[method-assign]
