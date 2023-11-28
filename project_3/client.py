import json

import branch_pb2_grpc
import grpc
from branch_pb2 import MsgDeliveryRequest, RequestElement
from google.protobuf.json_format import MessageToDict


class Client:
    def __init__(self, id, events):
        self.id = id
        self.events = events
        self.recvMsg = []
        self.stub = None

    def create_stub(self, destination_id):
        print("Creating stub for dest id:{}".format(destination_id))
        channel = 5000 + destination_id
        channel_name = "localhost:" + str(channel)
        channel = grpc.insecure_channel(channel_name)
        stub = branch_pb2_grpc.BranchStub(channel)
        return stub

    def execute_events(self):
        for event in self.events:
            request_data = []
            stub = self.create_stub(event["dest"])
            request_data.append(
                RequestElement(
                    id=event["id"],
                    interface=event["interface"],
                    money=event.get("money"),
                ),
            )
            request = MsgDeliveryRequest(request_elements=request_data)
            response = stub.MsgDelivery(request)
            self.recvMsg.append(response)

    def __repr__(self):
        return "Client:{}".format(self.id)


if __name__ == "__main__":
    # Monotonic writes
    f = open("monotonic_writes_input.json")
    customer_processes_request = json.load(f)

    customer_response = []
    for customer_processes_request in customer_processes_request:
        if customer_processes_request["type"] == "customer":
            client = Client(
                id=customer_processes_request["id"],
                events=customer_processes_request["events"],
            )
            client.execute_events()

            for customer_response_message in client.recvMsg:
                customer_response_dict = MessageToDict(
                    customer_response_message,
                    including_default_value_fields=True,
                )
                if customer_response_dict["recv"][0]["interface"] == "query":
                    output_response = {
                        "id": client.id,
                        "balance": customer_response_dict["recv"][0][
                            "result"
                        ]["balance"],
                    }
                    json_file_path = "monotonic_writes_output.json"
                    with open(json_file_path, "a") as monotonic_writes_output:
                        json.dump(
                            output_response, monotonic_writes_output, indent=2
                        )
                customer_response.append(customer_response_dict)

    # Read your writes
    f = open("read_your_writes_input.json")
    customer_processes_request = json.load(f)

    customer_response = []
    for customer_processes_request in customer_processes_request:
        if customer_processes_request["type"] == "customer":
            client = Client(
                id=customer_processes_request["id"],
                events=customer_processes_request["events"],
            )
            client.execute_events()

            for customer_response_message in client.recvMsg:
                customer_response_dict = MessageToDict(
                    customer_response_message,
                    including_default_value_fields=True,
                )
                if customer_response_dict["recv"][0]["interface"] == "query":
                    output_response = {
                        "id": client.id,
                        "balance": customer_response_dict["recv"][0][
                            "result"
                        ]["balance"],
                    }
                    json_file_path = "read_your_writes_output.json"
                    with open(json_file_path, "a") as monotonic_writes_output:
                        json.dump(
                            output_response, monotonic_writes_output, indent=2
                        )
                customer_response.append(customer_response_dict)
