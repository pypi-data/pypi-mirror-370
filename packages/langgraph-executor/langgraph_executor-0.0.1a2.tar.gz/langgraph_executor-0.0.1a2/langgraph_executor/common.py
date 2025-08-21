import traceback
from collections.abc import Mapping, Sequence
from collections.abc import Sequence as SequenceType
from typing import Any, cast

from google.protobuf.json_format import MessageToDict
from langchain_core.runnables import RunnableConfig
from langgraph._internal._constants import (
    CONFIG_KEY_CHECKPOINT_ID,
    CONFIG_KEY_CHECKPOINT_MAP,
    CONFIG_KEY_CHECKPOINT_NS,
    CONFIG_KEY_DURABILITY,
    CONFIG_KEY_RESUME_MAP,
    CONFIG_KEY_RESUMING,
    CONFIG_KEY_TASK_ID,
    CONFIG_KEY_THREAD_ID,
    TASKS,
)
from langgraph._internal._scratchpad import PregelScratchpad
from langgraph._internal._typing import MISSING
from langgraph.channels.base import BaseChannel, EmptyChannelError
from langgraph.checkpoint.base import Checkpoint, PendingWrite
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.errors import GraphBubbleUp, GraphInterrupt
from langgraph.managed.base import ManagedValue, ManagedValueMapping
from langgraph.pregel import Pregel
from langgraph.pregel._algo import PregelTaskWrites
from langgraph.pregel._read import PregelNode
from langgraph.types import Command, Interrupt, Send

from langgraph_executor.pb import types_pb2


def map_reserved_configurable(
    reserved_configurable: types_pb2.ReservedConfigurable,
) -> dict[str, Any]:
    # serde = JsonPlusSerializer()

    return {
        CONFIG_KEY_RESUMING: reserved_configurable.resuming,
        CONFIG_KEY_TASK_ID: reserved_configurable.task_id,
        CONFIG_KEY_THREAD_ID: reserved_configurable.thread_id,
        CONFIG_KEY_CHECKPOINT_MAP: reserved_configurable.checkpoint_map,
        CONFIG_KEY_CHECKPOINT_ID: reserved_configurable.checkpoint_id,
        CONFIG_KEY_CHECKPOINT_NS: reserved_configurable.checkpoint_ns,
        CONFIG_KEY_RESUME_MAP: {
            k: pb_to_val(v) for k, v in reserved_configurable.resume_map.items()
        }
        if reserved_configurable.resume_map
        else None,
        # CONFIG_KEY_PREVIOUS: serde.loads_typed( TODO
        #     (
        #         reserved_configurable.previous.method,
        #         reserved_configurable.previous.value,
        #     )
        # )
        # if reserved_configurable.previous
        # and reserved_configurable.previous.method != "missing"
        # else None,
        CONFIG_KEY_DURABILITY: reserved_configurable.durability,
    }


def reconstruct_config(pb_config: types_pb2.RunnableConfig) -> RunnableConfig:
    configurable = MessageToDict(pb_config.configurable)
    for k, v in map_reserved_configurable(pb_config.reserved_configurable).items():
        if v or k not in configurable:
            configurable[k] = v
    return RunnableConfig(
        tags=list(pb_config.tags),
        metadata=MessageToDict(pb_config.metadata),
        run_name=pb_config.run_name,
        run_id=pb_config.run_id,
        max_concurrency=pb_config.max_concurrency,
        recursion_limit=pb_config.recursion_limit,
        configurable=configurable,
    )


def revive_channel(channel: BaseChannel, channel_pb: types_pb2.Channel) -> BaseChannel:
    val_pb = channel_pb.checkpoint_result
    val = pb_to_val(val_pb)

    return channel.copy().from_checkpoint(val)


def reconstruct_channels(
    channels_pb: dict[str, types_pb2.Channel],
    graph: Pregel,
    scratchpad: PregelScratchpad,
) -> tuple[dict[str, BaseChannel], ManagedValueMapping]:
    channels = {}
    managed = {}
    for k, v in graph.channels.items():
        if isinstance(v, BaseChannel):
            assert k in channels_pb
            channels[k] = revive_channel(v, channels_pb[k])
        elif isinstance(v, ManagedValue) and scratchpad is not None:  # managed values
            managed[k] = v.get(scratchpad)
        else:
            raise NotImplementedError(f"Unrecognized channel value: {type(v)}")

    return channels, managed


def reconstruct_checkpoint(request_checkpoint: types_pb2.Checkpoint) -> Checkpoint:
    channel_versions = dict(request_checkpoint.channel_versions)
    versions_seen = {
        k: dict(v.channel_versions) for k, v in request_checkpoint.versions_seen.items()
    }
    # channel_values = unwrap_channel_values(request_checkpoint.channel_values)

    return Checkpoint(
        v=request_checkpoint.v,
        id=request_checkpoint.id,
        channel_versions=channel_versions,
        # channel_values=channel_values,
        versions_seen=versions_seen,
        ts=request_checkpoint.ts,
    )


def reconstruct_task_writes(
    request_tasks: SequenceType[Any],
) -> SequenceType[PregelTaskWrites]:
    # serde = JsonPlusSerializer()
    return [
        PregelTaskWrites(
            tuple(t.task_path),
            t.name,
            [(w.channel, pb_to_val(w.value)) for w in t.writes],
            t.triggers,
        )
        for t in request_tasks
    ]


def checkpoint_to_proto(checkpoint: Checkpoint) -> types_pb2.Checkpoint:
    checkpoint_proto = types_pb2.Checkpoint()
    checkpoint_proto.channel_versions.update(checkpoint["channel_versions"])
    for node, versions_dict in checkpoint["versions_seen"].items():
        checkpoint_proto.versions_seen[node].channel_versions.update(versions_dict)

    return checkpoint_proto


def updates_to_proto(
    checkpoint_proto: types_pb2.Checkpoint,
    updated_channel_names: Sequence[str],
    channels: types_pb2.Channels,
) -> types_pb2.Updates:
    return types_pb2.Updates(
        checkpoint=checkpoint_proto,
        updated_channels=updated_channel_names,
        channels=channels,
    )


def get_graph(
    graph_name: str,
    graphs: dict[str, Pregel],
) -> Pregel:
    if graph_name not in graphs:
        raise ValueError(f"Graph {graph_name} not supported")
    return graphs[graph_name]


def get_node(node_name: str, graph: Pregel, graph_name: str) -> PregelNode:
    if node_name not in graph.nodes:
        raise ValueError(f"Node {node_name} not found in graph {graph_name}")
    return graph.nodes[node_name]


def pb_to_val(value: types_pb2.Value) -> Any:
    serde = JsonPlusSerializer()

    value_kind = value.WhichOneof("message")
    if value_kind == "base_value":
        return serde.loads_typed((value.base_value.method, value.base_value.value))
    if value_kind == "sends":
        sends = []
        for send in value.sends.sends:
            node = send.node
            arg = pb_to_val(send.arg)
            sends.append(Send(node, arg))
        return sends
    if value_kind == "missing":
        return MISSING
    if value_kind == "command":
        graph, update, resume, goto = None, None, None, ()
        if value.command.graph is not None:
            graph = value.command.graph
        if value.command.update is not None:
            if (
                isinstance(value.command.update, dict)
                and len(value.command.update) == 1
                and "__root__" in value.command.update
            ):
                update = pb_to_val(value.command.update["__root__"])
            else:
                update = {k: pb_to_val(v) for k, v in value.command.update.items()}
        if value.command.resume:
            which = value.command.resume.WhichOneof("message")
            if which == "value":
                resume = pb_to_val(value.command.resume.value)
            else:
                resume_map = {
                    k: pb_to_val(v)
                    for k, v in value.command.resume.values.values.items()
                }
                resume = resume_map
        if value.command.gotos:
            gotos = []
            for g in value.command.gotos:
                which = g.WhichOneof("message")
                if which == "node_name":
                    gotos.append(g.node_name.name)
                else:
                    gotos.append(Send(g.send.node, pb_to_val(g.send.arg)))
            if len(gotos) == 1:
                gotos = gotos[0]
            goto = gotos
        return Command(graph=graph, update=update, resume=resume, goto=goto)
    raise NotImplementedError(f"Unrecognized value kind: {value_kind}")


def send_to_pb(send: Send) -> types_pb2.Send:
    return types_pb2.Send(
        node=send.node,
        arg=val_to_pb(TASKS if isinstance(send.arg, Send) else None, send.arg),
    )


def sends_to_pb(sends: list[Send]) -> types_pb2.Value:
    if not sends:
        return missing_to_pb()
    pb = []
    for send in sends:
        pb.append(send_to_pb(send))

    return types_pb2.Value(sends=types_pb2.Sends(sends=pb))


def command_to_pb(cmd: Command) -> types_pb2.Value:
    cmd_pb = types_pb2.Command()
    if cmd.graph:
        if not cmd.graph == Command.PARENT:
            raise ValueError("command graph must be null or parent")
        cmd_pb.graph = cmd.graph
    if cmd.update:
        if isinstance(cmd.update, dict):
            cmd_pb.update.update({k: val_to_pb(None, v) for k, v in cmd.update.items()})
        else:
            cmd_pb.update.update({"__root__": val_to_pb(None, cmd.update)})
    if cmd.resume:
        if isinstance(cmd.resume, dict):
            cmd_pb.resume.CopyFrom(resume_map_to_pb(cmd.resume))
        else:
            resume_val = types_pb2.Resume(value=val_to_pb(None, cmd.resume))
            cmd_pb.resume.CopyFrom(resume_val)
    if cmd.goto:
        gotos = []
        goto = cmd.goto
        if isinstance(goto, list):
            for g in goto:
                gotos.append(goto_to_pb(g))
        else:
            gotos.append(goto_to_pb(cast(Send | str, goto)))
        cmd_pb.gotos.extend(gotos)

    return types_pb2.Value(command=cmd_pb)


def resume_map_to_pb(resume: dict[str, Any] | Any) -> types_pb2.Resume:
    vals = {k: val_to_pb(None, v) for k, v in resume.items()}
    return types_pb2.Resume(values=types_pb2.InterruptValues(values=vals))


def goto_to_pb(goto: Send | str) -> types_pb2.Goto:
    if isinstance(goto, Send):
        return types_pb2.Goto(send=send_to_pb(goto))
    if isinstance(goto, str):
        return types_pb2.Goto(node_name=types_pb2.NodeName(name=goto))
    raise ValueError("goto must be send or node name")


def missing_to_pb() -> types_pb2.Value:
    pb = types_pb2.Value()
    pb.missing.SetInParent()
    return pb


def base_value_to_pb(value: Any) -> types_pb2.Value:
    serialized_value = serialize_value(value)

    return types_pb2.Value(base_value=serialized_value)


def serialize_value(value: Any) -> types_pb2.SerializedValue:
    serde = JsonPlusSerializer()

    meth, ser_val = serde.dumps_typed(value)
    return types_pb2.SerializedValue(method=meth, value=bytes(ser_val))


def val_to_pb(channel_name: str | None, value: Any) -> types_pb2.Value:
    if channel_name == TASKS and value != MISSING:
        if not isinstance(value, list):
            if not isinstance(value, Send):
                raise ValueError(
                    "Task must be a Send object objects."
                    f" Got type={type(value)} value={value}",
                )
            value = [value]
        else:
            for v in value:
                if not isinstance(v, Send):
                    raise ValueError(
                        "Task must be a list of Send objects."
                        f" Got types={[type(v) for v in value]} values={value}",
                    )
        return sends_to_pb(value)
    if value == MISSING:
        return missing_to_pb()
    if isinstance(value, Command):
        return command_to_pb(value)
    return base_value_to_pb(value)


def extract_channel(name: str, channel: BaseChannel) -> types_pb2.Channel:
    try:
        get_result = channel.get()
    except EmptyChannelError:
        get_result = MISSING

    return types_pb2.Channel(
        get_result=val_to_pb(name, get_result),
        is_available_result=channel.is_available(),
        checkpoint_result=val_to_pb(name, channel.checkpoint()),
    )


def extract_channels(
    channels: Mapping[str, BaseChannel | type[ManagedValue]],
) -> types_pb2.Channels:
    pb = {}
    for name, channel in channels.items():
        if isinstance(channel, BaseChannel):
            pb[name] = extract_channel(name, channel)
    return types_pb2.Channels(channels=pb)


def exception_to_pb(exc: Exception) -> types_pb2.ExecutorError:
    executor_error_pb = None
    if isinstance(exc, GraphInterrupt):
        if exc.args[0]:
            interrupts = [interrupt_to_pb(interrupt) for interrupt in exc.args[0]]
            graph_interrupt_pb = types_pb2.GraphInterrupt(
                interrupts=interrupts,
                interrupts_serialized=serialize_value(
                    exc.args[0] if len(exc.args[0]) != 1 else exc.args[0][0],
                ),  # brittle fix
            )
        else:
            graph_interrupt_pb = types_pb2.GraphInterrupt()
        executor_error_pb = types_pb2.ExecutorError(graph_interrupt=graph_interrupt_pb)
    elif isinstance(exc, GraphBubbleUp):
        bubbleup_pb = types_pb2.GraphBubbleUp()
        executor_error_pb = types_pb2.ExecutorError(graph_bubble_up=bubbleup_pb)
    else:
        base_error_pb = types_pb2.BaseError(
            error_type=str(type(exc)),
            error_message=str(exc),
            error_serialized=serialize_value(exc),
        )
        executor_error_pb = types_pb2.ExecutorError(base_error=base_error_pb)
        executor_error_pb.traceback = traceback.format_exc()

    return executor_error_pb


def interrupt_to_pb(interrupt: Interrupt) -> types_pb2.Interrupt:
    return types_pb2.Interrupt(
        value=val_to_pb(None, interrupt.value),
        id=interrupt.id,
    )


def pb_to_pending_writes(
    pb: SequenceType[types_pb2.PendingWrite],
) -> list[PendingWrite] | None:
    if not pb:
        return None

    return [(pw.task_id, pw.channel, pb_to_val(pw.value)) for pw in pb]
