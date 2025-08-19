import argparse
import logging
import os
import pathlib
import signal
import sys
import time
import uuid
from concurrent import futures

import grpc
from langgraph.pregel import Pregel

from langgraph_executor.executor import LangGraphExecutorServicer
from langgraph_executor.info_logger import ExecutorInfo, ExecutorInfoLogger
from langgraph_executor.pb.executor_pb2_grpc import (
    add_LangGraphExecutorServicer_to_server,
)

EXECUTOR_DEFAULT_PORT = 50052

EXECUTOR_INFO_FILE_NAME = "info.json"

YELLOW = "\033[93m"
RESET = "\033[0m"


class ColoredFormatter(logging.Formatter):
    def __init__(self, color=YELLOW, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.color = color

    def format(self, record):
        formatted_message = super().format(record)
        return f"{self.color}{formatted_message}{RESET}"


def setup_server_logging(component_id: str, debug=False, color=YELLOW):
    """Setup logging for server with executor ID label"""
    level = logging.DEBUG if debug else logging.INFO

    # Clear any existing handlers to prevent duplicates
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Configure logging
    logging.basicConfig(
        level=level,
        format=f"[{component_id}] %(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        force=True,
    )

    # Apply colored formatter to all handlers
    for handler in logging.root.handlers:
        handler.setFormatter(
            ColoredFormatter(
                color=color,
                fmt=f"[{component_id}] %(asctime)s [%(levelname)s] %(name)s: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            ),
        )


def create_executor_info(port: int, id: str):
    return ExecutorInfo(
        id=id,
        pid=os.getpid(),
        port=port,
        start_time=time.time(),
        status="starting",
        error_message=None,
        end_time=None,
    )


def signum_to_name(signum):
    try:
        return signal.Signals(signum).name
    except ValueError:
        return f"UNKNOWN_SIGNAL_{signum}"


def serve(
    graphs: dict[str, Pregel],
    port: int,
    debug: bool,
    id: str | None = None,
    log_dir: pathlib.Path | None = None,
):
    """Start the gRPC server.

    Args:
        graphs: Dictionary mapping graph names to compiled graphs
        port: Port to listen on

    """
    id_ = id
    if id_ is None:
        id_ = str(uuid.uuid4())

    setup_server_logging(f"EXECUTOR {id_}", debug=debug)
    logger = logging.getLogger(__name__)

    info_logger = ExecutorInfoLogger(
        log_dir or pathlib.Path(__file__).resolve().parent.parent / "logs",
    )

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_LangGraphExecutorServicer_to_server(LangGraphExecutorServicer(graphs), server)
    port = server.add_insecure_port(f"[::]:{port}")

    server.start()

    # Signal handler for graceful shutdown
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum_to_name(signum)}. Shutting down...")
        server.stop(5)  # Give 5 seconds for graceful shutdown
        info_logger.update_executor_info(
            executor_info.id,
            status="stopped",
            error_message=f"Shutdown via signal {signum_to_name(signum)}",
            end_time=time.time(),
        )
        logger.info("Shutdown complete")
        sys.exit(0)

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    executor_info = create_executor_info(port, id_)
    info_logger.write_executor_info(executor_info)

    try:
        info_logger.update_executor_info(executor_info.id, status="running")
        logger.info("Listening...")
        server.wait_for_termination()
    except Exception as e:
        logger.exception("Unexpected error in executor")
        server.stop(0)
        info_logger.update_executor_info(
            executor_info.id,
            status="error",
            error_message=str(e),
            end_time=time.time(),
        )
        raise


def main():
    """Start a LangGraph executor server."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=EXECUTOR_DEFAULT_PORT)
    parser.add_argument("--debug", action="store_true")
    parser.add_argument(
        "--log-dir",
        type=pathlib.Path,
        default=pathlib.Path(__file__).resolve().parents[2] / "logs",
    )

    args = parser.parse_args()

    id_ = str(uuid.uuid4())

    setup_server_logging(f"EXECUTOR {id_}", debug=args.debug)
    logging.getLogger(__name__)

    # load graphs. This is a cyclic dep just for demo purposes
    try:
        from langgraph_runtime_integration.graphs import (  # type: ignore[import-not-found]
            GRAPHS,  # type: ignore[import-untyped]
        )
    except ImportError:
        # Handle case where langgraph_runtime_integration is not available
        GRAPHS = {}

    graphs = GRAPHS

    # serve
    serve(graphs, args.port, args.debug, log_dir=args.log_dir)


if __name__ == "__main__":
    main()
