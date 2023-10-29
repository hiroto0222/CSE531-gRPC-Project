from time import sleep

import grpc

import branch_pb2_grpc
from branch_pb2 import MsgRequest


class Customer:
    def __init__(self, id, events):
        # unique ID of the Customer
        self.id = id
        # events from the input
        self.events = events
        # a list of received messages used for debugging purpose
        self.recvMsg = list()
        # pointer for the stub
        self.stub = None

    # Create gRPC channel and client stub for branch
    def createStub(self):
        port = str(50000 + self.id)
        channel = grpc.insecure_channel("localhost:" + port)
        self.stub = branch_pb2_grpc.BranchStub(channel)

    # Execute gRPC request for each event
    def executeEvents(self):
        for event in self.events:
            if event["interface"] == "query":
                sleep(3)

            # send req to branch
            res = self.stub.MsgDelivery(
                MsgRequest(
                    id=event["id"],
                    interface=event["interface"],
                    money=event["money"],
                )
            )

            # create msg
            msg = {"interface": res.interface, "result": res.result}
            if res.interface == "query":
                msg["money"] = res.money

            self.recvMsg.append(msg)

    def output(self):
        return {"id": self.id, "recv": self.recvMsg}
