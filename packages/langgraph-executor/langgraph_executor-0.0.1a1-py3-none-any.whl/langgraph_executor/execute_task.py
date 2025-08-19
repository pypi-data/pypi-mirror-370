from collections import deque
from dataclasses import is_dataclass
from functools import partial
from typing import Any

from langchain_core.runnables import RunnableConfig
from langgraph._internal._config import patch_config
from langgraph._internal._constants import (
    CACHE_NS_WRITES,
    CONF,
    CONFIG_KEY_CHECKPOINT_NS,
    CONFIG_KEY_READ,
    CONFIG_KEY_RESUME_MAP,
    CONFIG_KEY_RUNTIME,
    CONFIG_KEY_SCRATCHPAD,
    CONFIG_KEY_SEND,
    PULL,
    PUSH,
)
from langgraph._internal._scratchpad import PregelScratchpad
from langgraph.pregel import Pregel
from langgraph.pregel._algo import (
    PregelTaskWrites,
    _proc_input,
    _scratchpad,
    local_read,
)
from langgraph.pregel._call import identifier
from langgraph.runtime import DEFAULT_RUNTIME, Runtime
from langgraph.store.base import BaseStore
from langgraph.types import CacheKey, PregelExecutableTask
from pydantic import BaseModel
from xxhash import xxh3_128_hexdigest

from langgraph_executor.common import (
    get_node,
    pb_to_pending_writes,
    pb_to_val,
    reconstruct_channels,
    reconstruct_config,
    val_to_pb,
)
from langgraph_executor.pb import types_pb2


def get_init_request(request_iterator):
    request = next(request_iterator)

    if not hasattr(request, "init"):
        raise ValueError("First message must be init")

    return request.init


def reconstruct_task(
    request,
    graph: Pregel,
    *,
    store: BaseStore | None = None,
    config: RunnableConfig | None = None,
    custom_stream_writer=None,
) -> PregelExecutableTask:
    pb_task = request.task

    try:
        proc = get_node(pb_task.name, graph, pb_task.graph_name)
        if config is None:
            config = reconstruct_config(pb_task.config)
        configurable = config.get(CONF, {})

        scratchpad = create_scratchpad(
            config,
            pb_task,
            request.step,
            request.stop,
        )
        channels, managed = reconstruct_channels(
            request.channels.channels,
            graph,
            scratchpad,
        )
        if pb_task.task_path[0] == PULL:
            val = _proc_input(
                proc,
                managed,
                channels,
                for_execution=True,
                scratchpad=scratchpad,
                input_cache=None,
            )
        elif pb_task.task_path[0] == PUSH:
            val = pb_to_val(pb_task.input["PUSH_INPUT"])

        writes = deque()
        runtime = ensure_runtime(
            configurable, store, graph, custom_stream_writer=custom_stream_writer
        )

        # Generate cache key if cache policy exists
        cache_policy = getattr(proc, "cache_policy", None)
        cache_key = None
        if cache_policy:
            args_key = cache_policy.key_func(
                *([val] if not isinstance(val, list | tuple) else val),
            )
            cache_key = CacheKey(
                (CACHE_NS_WRITES, identifier(proc.node) or "__dynamic__"),
                xxh3_128_hexdigest(
                    args_key.encode() if isinstance(args_key, str) else args_key,
                ),
                cache_policy.ttl,
            )

        task = PregelExecutableTask(
            name=pb_task.name,
            input=val,
            proc=proc.node,
            writes=writes,
            config=patch_config(
                config,
                configurable={
                    CONFIG_KEY_SEND: writes.extend,
                    CONFIG_KEY_READ: partial(
                        local_read,
                        scratchpad,
                        channels,
                        managed,
                        PregelTaskWrites(
                            tuple(pb_task.task_path)[:3],
                            pb_task.name,
                            writes,
                            pb_task.triggers,
                        ),
                    ),
                    CONFIG_KEY_RUNTIME: runtime,
                    CONFIG_KEY_SCRATCHPAD: scratchpad,
                },
            ),
            triggers=pb_task.triggers,
            id=pb_task.id,
            path=pb_task.task_path,
            retry_policy=proc.retry_policy or [],  # TODO support
            cache_key=cache_key,  # TODO support
            writers=proc.flat_writers,
            subgraphs=proc.subgraphs,
        )

    except Exception as e:
        raise e

    return task


def extract_writes(writes) -> list[types_pb2.Write]:
    w = []
    for channel, val in writes:
        val_pb = val_to_pb(channel, val)
        channel_write = types_pb2.Write(channel=channel, value=val_pb)
        w.append(channel_write)

    return w


def create_scratchpad(
    config: RunnableConfig,
    pb_task: types_pb2.Task,
    step: int,
    stop: int,
) -> PregelScratchpad:
    task_checkpoint_ns: str = config[CONF].get(CONFIG_KEY_CHECKPOINT_NS) or ""
    pending_writes = (
        pb_to_pending_writes(pb_task.pending_writes)
        if (hasattr(pb_task, "pending_writes") and len(pb_task.pending_writes) > 0)
        else []
    )

    scratchpad = _scratchpad(
        config[CONF].get(CONFIG_KEY_SCRATCHPAD),
        pending_writes or [],
        pb_task.id,
        xxh3_128_hexdigest(task_checkpoint_ns.encode()),
        config[CONF].get(CONFIG_KEY_RESUME_MAP),
        step,
        stop,
    )

    return scratchpad


def ensure_runtime(configurable, store, graph, custom_stream_writer=None):
    runtime = configurable.get(CONFIG_KEY_RUNTIME)

    # Prepare runtime overrides
    overrides = {"store": store}
    if custom_stream_writer is not None:
        overrides["stream_writer"] = custom_stream_writer

    if runtime is None:
        return DEFAULT_RUNTIME.override(**overrides)
    if isinstance(runtime, Runtime):
        return runtime.override(**overrides)
    if isinstance(runtime, dict):
        context = _coerce_context(graph, runtime.get("context"))
        return Runtime(
            **(
                runtime
                | {"store": store, "context": context}
                | (
                    {"stream_writer": custom_stream_writer}
                    if custom_stream_writer
                    else {}
                )
            )
        )
    raise ValueError("Invalid runtime")


def _coerce_context(graph: Pregel, context: Any) -> Any:
    if context is None:
        return None

    context_schema = graph.context_schema
    if context_schema is None:
        return context

    schema_is_class = issubclass(context_schema, BaseModel) or is_dataclass(
        context_schema,
    )
    if isinstance(context, dict) and schema_is_class:
        return context_schema(**_filter_context_by_schema(context, graph))

    return context


_CACHE = {}


def _filter_context_by_schema(context: dict[str, Any], graph: Pregel) -> dict[str, Any]:
    if graph not in _CACHE:
        _CACHE[graph] = graph.get_context_jsonschema()
        if len(_CACHE) > 500:
            _CACHE.popitem()
    json_schema = _CACHE[graph]
    if not json_schema or not context:
        return context

    # Extract valid properties from the schema
    properties = json_schema.get("properties", {})
    if not properties:
        return context

    # Filter context to only include parameters defined in the schema
    filtered_context = {}
    for key, value in context.items():
        if key in properties:
            filtered_context[key] = value

    return filtered_context
