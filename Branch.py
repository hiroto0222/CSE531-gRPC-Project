import json
import sys
from concurrent import futures

import grpc
from termcolor import colored

import branch_pb2
import branch_pb2_grpc


# Branch class serves as gRPC service handler
class Branch(branch_pb2_grpc.BranchServicer):
    def __init__(self, id, balance, branches):
        self.id = id
        self.balance = balance
        self.branches = branches
        self.channels = []
        self.stubList = []
        self.recvMsg = []

    # Create channels and stubs for client
    def createStubs(self):
        for branch in self.branches:
            port = 50000 + branch
            channel = grpc.insecure_channel(f"localhost:{port}")
            self.channels.append(channel)
            stub = branch_pb2_grpc.BranchStub(channel)
            self.stubList.append(stub)

    # Process deposit request and return message
    def ProcessDeposit(self, request):
        self.balance += request.money
        if len(self.channels) == 0:
            self.createStubs()
        for stub in self.stubList:
            stub.MsgDelivery(
                branch_pb2.MsgDeliveryRequest(
                    balance=self.balance, interface="propagate_deposit"
                )
            )

        return {
            "id": self.id,
            "event_id": request.event_id,
            "result": "success",
        }

    # Process query request and return message
    def ProcessQuery(self, request):
        return {
            "id": self.id,
            "event_id": request.event_id,
            "balance": self.balance,
        }

    # Process withdraw request and return message
    def ProcessWithdraw(self, request):
        result = "fail"
        if self.balance >= request.money:
            result = "success"
            self.balance -= request.money
            if len(self.channels) == 0:
                self.createStubs()
            for stub in self.stubList:
                stub.MsgDelivery(
                    branch_pb2.MsgDeliveryRequest(
                        balance=self.balance, interface="propagate_withdraw"
                    )
                )

        return {"id": self.id, "event_id": request.event_id, "result": result}

    # Process propagate deposit and return message
    def ProcessPropagateDeposit(self, request):
        self.balance = request.balance
        return {"result": "success"}

    # Process propagate withdraw and return message
    def ProcessPropagateWithdraw(self, request):
        self.balance = request.balance
        return {"result": "success"}

    # Process recieved message
    def MsgDelivery(self, request, context):
        self.recvMsg.append(request)
        if request.interface == "query":
            msg = self.ProcessQuery(request=request)
        elif request.interface == "deposit":
            msg = self.ProcessDeposit(request=request)
        elif request.interface == "withdraw":
            msg = self.ProcessWithdraw(request=request)
        elif request.interface == "propagate_deposit":
            msg = self.ProcessPropagateDeposit(request=request)
        elif request.interface == "propagate_withdraw":
            msg = self.ProcessPropagateWithdraw(request=request)
        id = msg.get("id", None)
        event_id = msg.get("event_id", None)
        balance = msg.get("balance", None)
        result = msg.get("result", None)

        return branch_pb2.MsgDeliveryResponse(
            id=id, event_id=event_id, balance=balance, result=result
        )


# Start servers for each branch
def ServeBranches(branches):
    servers = []
    branchProcessIds = []

    for i in range(len(branches)):
        branchProcessIds.append(branches[i]["id"])

    for i in range(len(branches)):
        id = branches[i]["id"]
        balance = branches[i]["balance"]
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        branch = Branch(id=id, balance=balance, branches=branchProcessIds)
        branch_pb2_grpc.add_BranchServicer_to_server(branch, server)
        port = 50000 + id
        server.add_insecure_port(f"[::]:{port}")
        server.start()
        servers.append(server)
        print(
            colored(
                f"Branch {branches[i]['id']} started on port: {port}",
                "green",
            )
        )

    for server in servers:
        server.wait_for_termination()

    # stop servers on keyboard event
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print(colored("\nStop servers", "red"))
        for server in servers:
            server.stop(0)


if __name__ == "__main__":
    file_path = f"{sys.argv[1]}"
    with open(file_path, "r") as json_file:
        data = json.load(json_file)

    branches = []
    for i in range(len(data)):
        if data[i]["type"] == "branch":
            branches.append(data[i])

    ServeBranches(branches)
