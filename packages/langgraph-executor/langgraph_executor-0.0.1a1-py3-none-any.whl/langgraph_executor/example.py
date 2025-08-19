import grpc
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer

from langgraph_executor.pb import runtime_pb2, runtime_pb2_grpc, types_pb2

RUNTIME_SERVER_ADDRESS = "localhost:50051"

if __name__ == "__main__":
    channel = grpc.insecure_channel(RUNTIME_SERVER_ADDRESS)
    stub = runtime_pb2_grpc.LangGraphRuntimeStub(channel)

    serde = JsonPlusSerializer()
    input_raw = {"messages": ["hi"], "count": 0}
    method, ser = serde.dumps_typed(input_raw)
    input = types_pb2.SerializedValue(method=method, value=bytes(ser))

    request = runtime_pb2.InvokeRequest(
        graph_name="example",
        input=input,
        config=types_pb2.RunnableConfig(
            recursion_limit=25,
            max_concurrency=1,
            reserved_configurable=types_pb2.ReservedConfigurable(),
        ),
    )

    response = stub.Invoke(request)

    print("response: ", response)
