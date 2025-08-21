import asyncio
import contextlib
import functools
import logging
import uuid
from collections.abc import AsyncIterator, Callable, Collection, Iterator, Sequence
from typing import Any, Protocol, cast

import grpc
import grpc.aio
from google.protobuf.struct_pb2 import Struct  # type: ignore[import-untyped]
from langchain_core.messages import BaseMessage, BaseMessageChunk
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.base import Checkpoint
from langgraph.errors import GraphBubbleUp, GraphInterrupt
from langgraph.pregel import Pregel
from langgraph.pregel._algo import apply_writes
from langgraph.pregel._checkpoint import channels_from_checkpoint
from langgraph.pregel._retry import arun_with_retry
from langgraph.types import PregelExecutableTask

from langgraph_executor.common import (
    checkpoint_to_proto,
    exception_to_pb,
    extract_channels,
    pb_to_val,
    reconstruct_channels,
    reconstruct_checkpoint,
    reconstruct_config,
    reconstruct_task_writes,
    updates_to_proto,
)
from langgraph_executor.execute_task import (
    extract_writes,
    reconstruct_task,
)
from langgraph_executor.extract_graph import extract_graph
from langgraph_executor.pb import executor_pb2, executor_pb2_grpc, types_pb2
from langgraph_executor.stream_utils import ExecutorStreamHandler


class Logger(Protocol):
    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None: ...
    def info(self, msg: str, *args: Any, **kwargs: Any) -> None: ...
    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None: ...
    def error(self, msg: str, *args: Any, **kwargs: Any) -> None: ...
    def exception(self, msg: str, *args: Any, **kwargs: Any) -> None: ...
    def critical(self, msg: str, *args: Any, **kwargs: Any) -> None: ...


LOGGER = logging.getLogger(__name__)
SENTINEL = cast(executor_pb2.ExecuteTaskResponse, object())
GetGraph = Callable[
    [str, RunnableConfig], contextlib.AbstractAsyncContextManager[Pregel]
]


class LangGraphExecutorServicer(executor_pb2_grpc.LangGraphExecutorServicer):
    """gRPC servicer for LangGraph runtime execution operations."""

    def __init__(
        self,
        graphs: Collection[str],
        *,
        subgraph_map: dict[str, str],
        get_graph: GetGraph,
        logger: Logger | None = None,
    ):
        """Initialize the servicer with compiled graphs.

        Args:
            graphs: Dictionary mapping graph names to compiled graphs
            subgraph_map: Dictionary mapping subgraph names to parent graph names
            get_graph: Function to get a graph by name
            logger: Optional logger

        """
        self.logger = logger or LOGGER
        self.graphs = set(graphs)
        self.graph_names = sorted(self.graphs)
        self.subgraph_map = subgraph_map
        self.get_graph = get_graph
        _patch_base_message_with_ids()
        self._graph_definition_cache: dict[str, executor_pb2.GetGraphResponse] = {}

    async def ListGraphs(
        self, request: Any, context: grpc.aio.ServicerContext
    ) -> executor_pb2.ListGraphsResponse:  # type: ignore[name-defined]
        """List available graphs."""
        return executor_pb2.ListGraphsResponse(
            graph_names=self.graph_names,
        )

    async def GetGraph(
        self, request: Any, context: grpc.aio.ServicerContext
    ) -> executor_pb2.GetGraphResponse:  # type: ignore[name-defined]
        """Get graph definition."""
        try:
            self.logger.debug("GetGraph called")
            graph_name: str = request.graph_name
            return await self._get_graph_definition(graph_name)

        except Exception as e:
            self.logger.error(f"GetGraph Error: {e}", exc_info=True)
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

    async def _get_graph_definition(self, name: str) -> executor_pb2.GetGraphResponse:
        if (resp := self._graph_definition_cache.get(name)) is not None:
            return resp
        async with self.get_graph(name, RunnableConfig()) as graph:
            graph_definition = extract_graph(graph)

            resp = executor_pb2.GetGraphResponse(
                graph_definition=graph_definition,
                parent_name=self.subgraph_map.get(name, None),
                checkpointer=graph.checkpointer is not None,
            )
            self._graph_definition_cache[name] = resp
            return resp

    async def GetAllGraphs(
        self,
        request: executor_pb2.GetAllGraphsRequest,
        context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[executor_pb2.GetGraphResponse]:
        try:
            self.logger.debug("GetAllGraphs called")
            for name in self.graph_names:
                yield await self._get_graph_definition(name)

        except Exception as e:
            self.logger.error(f"GetAllGraphs Error: {e}", exc_info=True)
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

    async def ChannelsFromCheckpoint(
        self, request: Any, context: grpc.aio.ServicerContext
    ) -> executor_pb2.ChannelsFromCheckpointResponse:  # type: ignore[name-defined]
        try:
            self.logger.debug("ChannelsFromCheckpoint called")
            async with self.get_graph(request.graph_name, RunnableConfig()) as graph:
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
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

    async def ExecuteTask(
        self,
        request_iterator: Iterator[executor_pb2.ExecuteTaskRequest],  # type: ignore[name-defined]
        context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[executor_pb2.ExecuteTaskResponse]:  # type: ignore[name-defined]
        self.logger.debug("ExecuteTask called")

        # Right now, only handle task execution without interrupts, etc
        try:
            request = await _get_init_request(request_iterator)
            config = reconstruct_config(request.task.config)
            async with self.get_graph(request.graph_name, config) as graph:
                stream_messages = "messages" in request.stream_modes
                stream_custom = "custom" in request.stream_modes

                stream_queue = asyncio.Queue()

                custom_stream_writer = (
                    _create_custom_stream_writer(stream_queue, self.logger)
                    if stream_custom
                    else None
                )

                task = reconstruct_task(
                    request, graph, custom_stream_writer=custom_stream_writer
                )
                if stream_messages:
                    # Create and inject callback handler
                    stream_handler = ExecutorStreamHandler(
                        functools.partial(
                            stream_callback,
                            logger=self.logger,
                            stream_queue=stream_queue,
                        ),
                        task.id,
                    )

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
                if should_execute:
                    runner_task = asyncio.create_task(
                        _run_task(task, logger=self.logger, stream_queue=stream_queue)
                    )
                    # Drain the queue and stream responses to client
                    while True:
                        item = await stream_queue.get()
                        if item is SENTINEL:
                            break
                        yield item
                    exception_pb = await runner_task

                # Ensure the final chat messages are emitted (if any)
                final_messages = _extract_output_messages(task.writes)
                if final_messages:
                    for message in final_messages:
                        yield executor_pb2.ExecuteTaskResponse(
                            message_or_message_chunk=message
                        )

                # Final task result
                yield executor_pb2.ExecuteTaskResponse(
                    task_result=executor_pb2.TaskResult(
                        error=exception_pb, writes=extract_writes(task.writes)
                    )
                )

        except Exception as e:
            self.logger.exception(f"ExecuteTask error: {e}")
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

    async def ApplyWrites(
        self, request: Any, context: grpc.aio.ServicerContext
    ) -> executor_pb2.ApplyWritesResponse:  # type: ignore[name-defined]
        # get graph
        self.logger.debug("ApplyWrites called")
        try:
            async with self.get_graph(request.graph_name, RunnableConfig()) as graph:
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
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

    async def GenerateCacheKey(
        self,
        request: executor_pb2.GenerateCacheKeyRequest,
        context: grpc.aio.ServicerContext,
    ) -> executor_pb2.GenerateCacheKeyResponse:
        """Generate cache key for a node execution"""
        raise NotImplementedError("GenerateCacheKey not implemented")


# Helpers


async def _run_task(
    task: PregelExecutableTask,
    *,
    logger: Logger,
    stream_queue: asyncio.Queue[executor_pb2.ExecuteTaskResponse],
) -> types_pb2.ExecutorError | None:
    try:
        await arun_with_retry(
            task,
            retry_policy=None,
        )

    except Exception as e:
        if isinstance(e, GraphBubbleUp | GraphInterrupt):
            logger.info(f"Interrupt in task {task.id}: {e}")
        else:
            logger.exception(
                f"Exception running task {task.id}: {e}\nTask: {task}\n\n",
                exc_info=True,
            )
        return exception_to_pb(e)
    finally:
        await stream_queue.put(SENTINEL)


def stream_callback(
    message: BaseMessageChunk,
    metadata: dict,
    *,
    logger: Logger,
    stream_queue: asyncio.Queue[executor_pb2.ExecuteTaskResponse],
):
    """Callback to capture stream chunks and queue them."""
    try:
        stream_queue.put_nowait(
            executor_pb2.ExecuteTaskResponse(
                message_or_message_chunk=_extract_output_message(message)
            )
        )
    except Exception as e:
        logger.warning(f"Failed to create stream chunk: {e}", exc_info=True)


def _create_custom_stream_writer(stream_queue: asyncio.Queue[Any], logger: Logger):
    """Create a proper stream_writer function for custom mode (like langgraph does)."""

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
            stream_queue.put_nowait(custom_event_response)

        except Exception as e:
            logger.warning(f"Failed to create custom stream event: {e}", exc_info=True)

    return stream_writer


def _extract_output_messages(writes: Sequence[Any]) -> list[types_pb2.Message]:  # type: ignore[name-defined]
    messages = []
    for write in writes:
        # Not sure this check is right
        if isinstance(write[1], BaseMessage):
            messages.append(_extract_output_message(write[1]))
        elif isinstance(write[1], Sequence):
            messages.extend(
                [
                    _extract_output_message(w)
                    for w in write[1]
                    if isinstance(w, BaseMessage)
                ]
            )

    return messages


def _extract_output_message(write: Any) -> types_pb2.Message:  # type: ignore[name-defined]
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


async def _get_init_request(request_iterator):
    request = await anext(request_iterator)

    if not hasattr(request, "init"):
        raise ValueError("First message must be init")

    return request.init


@functools.lru_cache(maxsize=1)
def _patch_base_message_with_ids() -> None:
    """Patch the specific BaseMessage class used in your system."""
    try:
        from langchain_core.messages import BaseMessage

        original_init = BaseMessage.__init__

        def patched_init(self, content: Any, **kwargs: Any) -> None:
            original_init(self, content, **kwargs)
            if self.id is None:
                self.id = str(uuid.uuid4())

        BaseMessage.__init__ = patched_init  # type: ignore[method-assign]
    except Exception as e:
        LOGGER.warning("Failed to patch BaseMessage with IDs: %s", e)
