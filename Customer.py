import json
import sys

import grpc
from termcolor import colored

import branch_pb2
import branch_pb2_grpc


class Customer:
    def __init__(self, id, events):
        self.id = id
        self.events = events
        self.recvMsg = []
        self.channel = None
        self.stub = None
        self.port = 50000 + id
        self.lastProcessedId = -1

    # Create client stub
    def createStub(self):
        self.channel = grpc.insecure_channel(f"localhost:{self.port}")
        self.stub = branch_pb2_grpc.BranchStub(self.channel)

    # Execute client called events
    def executeEvents(self):
        if not self.stub:
            self.createStub()

        res = {"id": self.id, "recv": []}

        for i in range(self.lastProcessedId + 1, len(self.events)):
            self.lastProcessedId = i
            print(
                colored(
                    f"processing {self.events[i]['interface']} Event with Index: {i}",
                    "yellow",
                )
            )
            curr_interface = self.events[i]["interface"]
            curr_event_id = self.events[i]["id"]

            if curr_interface == "deposit":
                response = self.stub.MsgDelivery(
                    branch_pb2.MsgDeliveryRequest(
                        id=self.id,
                        event_id=curr_event_id,
                        interface=curr_interface,
                        money=self.events[i]["money"],
                    )
                )
                res["recv"].append(
                    {"interface": curr_interface, "result": response.result}
                )

            elif curr_interface == "query":
                response = self.stub.MsgDelivery(
                    branch_pb2.MsgDeliveryRequest(
                        id=self.id,
                        event_id=curr_event_id,
                        interface=curr_interface,
                    )
                )
                res["recv"].append(
                    {"interface": curr_interface, "balance": response.balance}
                )

            elif curr_interface == "withdraw":
                response = self.stub.MsgDelivery(
                    branch_pb2.MsgDeliveryRequest(
                        id=self.id,
                        event_id=curr_event_id,
                        interface=curr_interface,
                        money=self.events[i]["money"],
                    )
                )
                res["recv"].append(
                    {"interface": curr_interface, "result": response.result}
                )

        return res


if __name__ == "__main__":
    file_path = f"{sys.argv[1]}"
    with open(file_path, "r") as json_file:
        data = json.load(json_file)

    res = []

    for i in range(len(data)):
        if data[i]["type"] == "customer":
            customer_id = data[i]["id"]
            customer = Customer(customer_id, data[i]["events"])
            res.append(customer.executeEvents())

    with open("output.json", "w") as json_file:
        json.dump(res, json_file)
