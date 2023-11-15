import json
import os
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
        self.clock = 0  # set initial logical clock as 0
        self.logs = {
            "id": self.id,
            "type": "branch",
            "events": [],
        }  # log branch events
        self.stubListBranches = []

    # Create channels and stubs for client
    def createStubs(self):
        for branch in self.branches:
            port = 50000 + branch
            channel = grpc.insecure_channel(f"localhost:{port}")
            self.channels.append(channel)
            stub = branch_pb2_grpc.BranchStub(channel)
            self.stubList.append(stub)
            self.stubListBranches.append(branch)

    def MsgDelivery(self, request, context):
        self.recvMsg.append(request)
        self.clock = max(self.clock, request.clock) + 1

        if request.interface == "query":
            res = self.Query(request=request)
        elif request.interface == "deposit":
            res = self.Deposit(request=request)
        elif request.interface == "withdraw":
            res = self.Withdraw(request=request)
        elif request.interface == "propagatewithdraw":
            res = self.PropagateWithdraw(request=request)
        elif request.interface == "propagatedeposit":
            res = self.PropagateDeposit(request=request)

        id = res.get("id", None)
        event_id = res.get("event_id", None)
        balance = res.get("balance", None)
        result = res.get("result", None)

        # dump logs
        filename = f"branch-{self.id}.json"
        output_path = os.path.join("output", filename)
        with open(output_path, "w") as file:
            json.dump(self.branch_logs, file, indent=4)

        return branch_pb2.MsgDeliveryResponse(
            id=id,
            event_id=event_id,
            balance=balance,
            result=result,
            clock=self.clock,
        )

    def Deposit(self, request):
        self.balance += request.money
        self.branch_logs["events"].append(
            {
                "customer-request-id": request.event_id,
                "logical_clock": self.clock,
                "interface": "deposit",
                "comment": f"event_recv from customer {request.id}",
            }
        )

        if len(self.channelList) == 0:
            self.createStubs()

        for i in range(len(self.stubList)):
            stub = self.stubList[i]
            recv_branch = self.stubListBranches[i]
            self.clock += 1
            self.branch_logs["events"].append(
                {
                    "customer-request-id": request.event_id,
                    "logical_clock": self.clock,
                    "interface": "propogate_deposit",
                    "comment": f"event_sent to branch {recv_branch}",
                }
            )
            stub.MsgDelivery(
                branch_pb2.MsgDeliveryRequest(
                    id=self.id,
                    event_id=request.event_id,
                    balance=self.balance,
                    interface="propagatedeposit",
                    clock=self.clock,
                )
            )

        return {
            "id": self.id,
            "event_id": request.event_id,
            "result": "success",
            "clock": self.clock,
        }

    def Query(self, request):
        return {
            "id": self.id,
            "event_id": request.event_id,
            "balance": self.balance,
            "clock": self.clock,
        }

    def Withdraw(self, request):
        self.branch_logs["events"].append(
            {
                "customer-request-id": request.event_id,
                "logical_clock": self.clock,
                "interface": "deposit",
                "comment": f"event_recv from customer {request.id}",
            }
        )

        status = "fail"
        if self.balance >= request.money:
            status = "success"
            self.balance -= request.money

            if len(self.channelList) == 0:
                self.createStubs()

            for i in range(len(self.stubList)):
                stub = self.stubList[i]
                recv_branch = self.stubListBranches[i]
                self.clock += 1
                self.branch_logs["events"].append(
                    {
                        "customer-request-id": request.event_id,
                        "logical_clock": self.clock,
                        "interface": "propogate_withdraw",
                        "comment": f"event_sent to branch {recv_branch}",
                    }
                )
                stub.MsgDelivery(
                    branch_pb2.MsgDeliveryRequest(
                        id=self.id,
                        event_id=request.event_id,
                        balance=self.balance,
                        interface="propagatewithdraw",
                        clock=self.clock,
                    )
                )
        return {"id": self.id, "event_id": request.event_id, "result": status}

    def Propagate_Deposit(self, request):
        self.balance = request.balance
        self.branch_logs["events"].append(
            {
                "customer-request-id": request.event_id,
                "logical_clock": self.clock,
                "interface": "propogate_deposit",
                "comment": f"event_recv from bank {request.id}",
            }
        )
        return {"result": "success"}

    def Propagate_Withdraw(self, request):
        self.balance = request.balance
        self.branch_logs["events"].append(
            {
                "customer-request-id": request.event_id,
                "logical_clock": self.clock,
                "interface": "propogate_withdraw",
                "comment": f"event_recv from bank {request.id}",
            }
        )
        return {"result": "success"}


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
