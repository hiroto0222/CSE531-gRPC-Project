import grpc

import branch_pb2_grpc
from branch_pb2 import MsgRequest, MsgResponse


class Branch(branch_pb2_grpc.RPCServicer):
    def __init__(self, id, balance, branches):
        # unique ID of the Branch
        self.id = id
        # replica of the Branch's balance
        self.balance = balance
        # the list of process IDs of the branches
        self.branches = branches
        # the list of Client stubs to communicate with the branches
        self.stubList = list()
        # a list of received messages used for debugging purpose
        self.recvMsg = list()
        # iterate the processID of the branches

    # Creates gRPC channel and client stub for each branch
    def createStubs(self):
        for branch_id in self.branches:
            if branch_id != self.id:
                port = str(50000 + branch_id)
                channel = grpc.insecure_channel("localhost:" + port)
                self.stubList.append(branch_pb2_grpc.BranchStub(channel))

    # Process incoming MsgRequest from customer transaction
    def MsgDelivery(self, request, context):
        return self.ProcessMsg(request, True)

    # Process incoming MsgRequest from branch propagation
    def MsgPropagation(self, request, context):
        return self.ProcessMsg(request, False)

    # Process received message and return a MsgResponse
    def ProcessMsg(self, request, propagate):
        res = "success"

        if request.money < 0:
            res = "fail"
        elif request.interface == "query":
            pass
        elif request.interface == "deposit":
            self.balance += request.money
            if propagate:
                self.PropagateDeposit(request)
        elif request.interface == "withdraw":
            if self.balance >= request.money:
                self.balance -= request.money
                if propagate:
                    self.PropagateWithdraw(request)
            else:
                res = "fail"
        else:
            res = "fail"

        # Generate Msg
        msg = {"interface": request.interface, "result": res}
        if request.interface == "query":
            msg["money"] = request.money

        self.recvMsg.append(msg)

        return MsgResponse(
            interface=request.interface, result=res, money=self.balance
        )

    # Propagate client deposit to other branches
    def PropagateDeposit(self, request):
        for stub in self.stubList:
            stub.MsgPropagation(
                MsgRequest(
                    id=request.id, interface="deposit", money=request.money
                )
            )

    # Propagate client withdraw to other branches
    def PropagateWithdraw(self, request):
        for stub in self.stubList:
            stub.MsgPropagation(
                MsgRequest(
                    id=request.id, interface="withdraw", money=request.money
                )
            )
