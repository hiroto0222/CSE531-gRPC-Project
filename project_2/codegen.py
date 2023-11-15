# Genrate gRPC code using grpc_tools.protoc

from grpc_tools import protoc

protoc.main(
    (
        "",
        "-I.",
        "--python_out=.",
        "--grpc_python_out=.",
        "./branch.proto",
    )
)
