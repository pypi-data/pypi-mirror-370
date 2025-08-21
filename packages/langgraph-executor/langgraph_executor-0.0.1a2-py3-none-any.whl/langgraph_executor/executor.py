import contextlib
import functools
import logging
from typing import Any

import grpc
import grpc.aio
from langgraph._internal._constants import NS_SEP
from langgraph.pregel import Pregel

from langgraph_executor.executor_base import LangGraphExecutorServicer
from langgraph_executor.pb.executor_pb2_grpc import (
    add_LangGraphExecutorServicer_to_server,
)

# Internal helpers
LOGGER = logging.getLogger(__name__)


def create_server(graphs: dict[str, Pregel], address: str) -> grpc.aio.Server:
    graphs, subgraph_map = _load_graphs(graphs)
    server = grpc.aio.server(
        # Be permissive: allow client pings without active RPCs and accept intervals
        # as low as 50s. Our clients still default to ~5m, but this avoids penalizing
        # other, more frequent clients.
        options=[
            ("grpc.keepalive_permit_without_calls", 1),
            ("grpc.http2.min_recv_ping_interval_without_data_ms", 50000),  # 50s
            ("grpc.http2.max_ping_strikes", 2),
        ]
    )
    getter = functools.partial(get_graph, graphs=graphs)
    add_LangGraphExecutorServicer_to_server(
        LangGraphExecutorServicer(graphs, subgraph_map=subgraph_map, get_graph=getter),
        server,
    )
    server.add_insecure_port(address)
    return server


@contextlib.asynccontextmanager
async def get_graph(graph_name: str, config: Any, *, graphs: dict[str, Pregel]):
    yield graphs[graph_name]


def _load_graphs(graphs: dict[str, Pregel]) -> tuple[dict[str, Pregel], dict[str, str]]:
    """Load graphs and their subgraphs recursively in hierarchical order.

    Args:
        graphs: Dictionary of root graphs to load
    """
    # First, ensure all root graphs have unique names
    _ensure_unique_root_names(graphs)
    subgraph_map: dict[str, str] = {}

    # Then, collect all subgraphs and mappings
    all_subgraphs: dict[str, Pregel] = {}
    subgraph_to_parent: dict[str, str] = {}

    for root_graph in graphs.values():
        subgraphs, mappings = _collect_subgraphs(root_graph, root_graph.name)
        all_subgraphs.update(subgraphs)
        subgraph_to_parent.update(mappings)

    subgraph_map.update(subgraph_to_parent)

    # Now build self.graphs in hierarchical order (parents before children)
    for root_name in sorted(graphs.keys()):
        _load_graph_and_children(
            root_name, graphs, {**graphs, **all_subgraphs}, subgraph_map
        )

    _log_supported_graphs(graphs, subgraph_map)
    return graphs, subgraph_map


def _ensure_unique_root_names(graphs: dict[str, Pregel]) -> None:
    """Ensure all root graphs have unique names"""
    seen_names = set()

    for name in graphs:
        if name in seen_names:
            raise ValueError(
                f"Root graph name conflict detected: {name}. Root graphs must have unique names"
            )
        seen_names.add(name)


def _collect_subgraphs(
    graph: Pregel, namespace: str
) -> tuple[dict[str, Pregel], dict[str, str]]:
    """Recursively collect all subgraphs from a root graph"""
    subgraphs = {}
    mappings = {}

    for idx, (node_name, subgraph) in enumerate(graph.get_subgraphs(recurse=False)):
        # Generate subgraph name
        subgraph.name = f"{namespace}{NS_SEP}{node_name}{NS_SEP}{idx}"

        # Add this subgraph
        subgraphs[subgraph.name] = subgraph
        mappings[subgraph.name] = graph.name

        # Recursively process this subgraph's children
        nested_subgraphs, nested_mappings = _collect_subgraphs(subgraph, namespace)

        subgraphs.update(nested_subgraphs)
        mappings.update(nested_mappings)

    return subgraphs, mappings


def _load_graph_and_children(
    graph_name: str,
    graphs: dict[str, Pregel],
    all_graphs: dict[str, Pregel],
    subgraph_map: dict[str, str],
) -> None:
    """Recursively add a graph and its children to self.graphs in order"""

    # Add this graph to self.graphs (maintaining insertion order)
    graphs[graph_name] = all_graphs[graph_name]

    # Get direct children of this graph
    children = [
        child_name
        for child_name, parent_name in subgraph_map.items()
        if parent_name == graph_name
    ]

    # Add children in sorted order (for deterministic output)
    for child_name in sorted(children):
        _load_graph_and_children(child_name, graphs, all_graphs, subgraph_map)


def _log_supported_graphs(
    graphs: dict[str, Pregel], subgraph_map: dict[str, str]
) -> None:
    """Log the complete graph hierarchy in a tree-like format."""
    LOGGER.info("Loaded graphs:")

    # Get root graphs
    root_graphs = {name for name in graphs if name not in subgraph_map}

    for root_name in sorted(root_graphs):
        LOGGER.info(f"  {root_name}")
        _log_graph_children(root_name, subgraph_map, indent=2)


def _log_graph_children(
    parent_name: str, subgraph_map: dict[str, str], *, indent: int = 0
) -> None:
    """Recursively log children of a graph with proper indentation."""
    children = [
        child for child, parent in subgraph_map.items() if parent == parent_name
    ]

    for child in sorted(children):
        prefix = "  " * indent + "└─ "
        LOGGER.info(f"{prefix}{child}")
        # Recursively log this child's children
        _log_graph_children(child, subgraph_map, indent=indent + 1)
