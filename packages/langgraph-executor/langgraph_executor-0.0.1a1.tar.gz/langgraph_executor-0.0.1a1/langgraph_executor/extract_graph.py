"""Shared module for extracting graph information from LangGraph graphs."""

from collections.abc import Sequence
from typing import Any

from google.protobuf.json_format import MessageToJson
from google.protobuf.struct_pb2 import Struct  # type: ignore[import-not-found]
from langchain_core.runnables import RunnableConfig
from langgraph._internal._constants import (  # CONFIG_KEY_PREVIOUS,
    CONFIG_KEY_CHECKPOINT_ID,
    CONFIG_KEY_CHECKPOINT_MAP,
    CONFIG_KEY_CHECKPOINT_NS,
    CONFIG_KEY_DURABILITY,
    CONFIG_KEY_RESUMING,
    CONFIG_KEY_TASK_ID,
    CONFIG_KEY_THREAD_ID,
    RESERVED,
)
from langgraph.cache.memory import InMemoryCache
from langgraph.pregel import Pregel
from langgraph.pregel._read import PregelNode
from langgraph.utils.config import ensure_config

from langgraph_executor.common import extract_channels
from langgraph_executor.pb import graph_pb2, types_pb2

DEFAULT_MAX_CONCURRENCY = 1


def extract_cache_type(cache: Any) -> str:
    """Extract cache type from a cache object."""
    if cache is None:
        return "unsupported"
    if isinstance(cache, InMemoryCache):
        return "inMemory"
    return "unsupported"


def extract_config(config: RunnableConfig) -> types_pb2.RunnableConfig:
    ensured_config = ensure_config(config)
    # metadata
    metadata_proto = Struct()
    metadata = {k: v for k, v in ensured_config["metadata"].items()}
    metadata_proto.update(metadata)
    # configurable
    configurable_proto = Struct()

    configurable = {}
    for k, v in ensured_config["configurable"].items():
        if k not in RESERVED:
            configurable[k] = v

    configurable_proto.update(configurable)
    return types_pb2.RunnableConfig(
        tags=[t for t in ensured_config["tags"]],
        recursion_limit=ensured_config["recursion_limit"],
        run_name=ensured_config.get("run_name", ""),
        max_concurrency=(
            ensured_config.get("max_concurrency", DEFAULT_MAX_CONCURRENCY)
        ),
        metadata=metadata_proto,
        configurable=configurable_proto,
        reserved_configurable=extract_reserved_configurable(
            config.get("configurable", {})
        ),
    )


def extract_reserved_configurable(
    configurable: dict[str, Any],
) -> types_pb2.ReservedConfigurable:
    return types_pb2.ReservedConfigurable(
        resuming=bool(configurable.get(CONFIG_KEY_RESUMING, False)),
        task_id=str(configurable.get(CONFIG_KEY_TASK_ID, "")),
        thread_id=str(configurable.get(CONFIG_KEY_THREAD_ID, "")),
        checkpoint_map=dict(configurable.get(CONFIG_KEY_CHECKPOINT_MAP, {})),
        checkpoint_id=str(configurable.get(CONFIG_KEY_CHECKPOINT_ID, "")),
        checkpoint_ns=str(configurable.get(CONFIG_KEY_CHECKPOINT_NS, "")),
        durability=configurable.get(CONFIG_KEY_DURABILITY, "async"),
    )


def extract_nodes(nodes: dict[str, PregelNode]) -> list[graph_pb2.NodeDefinition]:
    return [extract_node(k, v) for k, v in nodes.items()]


def extract_node(name: str, node: PregelNode) -> graph_pb2.NodeDefinition:
    if isinstance(node.channels, str):
        channels = [node.channels]
    elif isinstance(node.channels, list):
        channels = node.channels
    elif isinstance(node.channels, dict):
        channels = [k for k, _ in node.channels.items()]
    else:
        channels = []
    # TODO cache policy
    return graph_pb2.NodeDefinition(
        metadata=Struct(fields=node.metadata or {}),
        name=name,
        triggers=node.triggers,
        tags=node.tags or [],
        channels=channels,
    )


def extract_trigger_to_nodes(
    trigger_to_nodes: dict[str, Sequence[str]] | Any,  # Allow Mapping type from graph
) -> dict[str, graph_pb2.TriggerMapping]:
    trigger_map = {}
    for trigger, nodes in trigger_to_nodes.items():
        if isinstance(nodes, dict) and "nodes" in nodes:
            trigger_map[trigger] = graph_pb2.TriggerMapping(nodes=nodes["nodes"])
        elif isinstance(nodes, list):
            trigger_map[trigger] = graph_pb2.TriggerMapping(nodes=nodes)
        else:
            trigger_map[trigger] = graph_pb2.TriggerMapping(nodes=[])
    return trigger_map


def extract_graph(graph: Pregel) -> graph_pb2.GraphDefinition:
    """Extract graph information from a compiled LangGraph graph.

    Returns a protobuf message that contains all relevant orchestration information about the graph
    """
    # Handle input_channels and output_channels oneof
    graph_def = graph_pb2.GraphDefinition(
        name=str(graph.name),
        channels=extract_channels(graph.channels),
        interrupt_before_nodes=list(graph.interrupt_before_nodes),
        interrupt_after_nodes=list(graph.interrupt_after_nodes),
        stream_mode=(
            [graph.stream_mode]
            if isinstance(graph.stream_mode, str)
            else graph.stream_mode
        ),
        stream_eager=bool(graph.stream_eager),
        stream_channels=(
            [graph.stream_channels]
            if isinstance(graph.stream_channels, str)
            else list(graph.stream_channels)
            if graph.stream_channels
            else []
        ),
        step_timeout=float(graph.step_timeout) if graph.step_timeout else 0.0,
        debug=bool(graph.debug),
        # TODO retry policy
        cache=graph_pb2.Cache(
            cache_type=extract_cache_type(getattr(graph, "cache", None)),
        ),
        config=extract_config(graph.config) if graph.config else None,
        nodes=extract_nodes(graph.nodes),
        trigger_to_nodes=extract_trigger_to_nodes(graph.trigger_to_nodes),
    )

    # Set input_channels and input_channels_is_list flag based on type
    if isinstance(graph.input_channels, str):
        graph_def.input_channels.extend([graph.input_channels])
        graph_def.input_channels_is_list = False
    else:
        graph_def.input_channels.extend(graph.input_channels)
        graph_def.input_channels_is_list = True

    # Set output_channels and output_channels_is_list flag based on type
    if isinstance(graph.output_channels, str):
        graph_def.output_channels.extend([graph.output_channels])
        graph_def.output_channels_is_list = False
    else:
        graph_def.output_channels.extend(graph.output_channels)
        graph_def.output_channels_is_list = True

    return graph_def


def convert_to_json(proto):
    return MessageToJson(proto)
