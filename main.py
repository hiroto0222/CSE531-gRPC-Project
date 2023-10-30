import argparse
import json
import multiprocessing
from concurrent import futures
from time import sleep

import grpc
from termcolor import colored

import branch_pb2_grpc
from Branch import Branch
from Customer import Customer


# Branch gRPC server
def serveBranch(branch):
    branch.createStubs()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    branch_pb2_grpc.add_BranchServicer_to_server(branch, server)
    port = str(50000 + branch.id)
    server.add_insecure_port("[::]:" + port)
    server.start()
    server.wait_for_termination()


# Customer gRPC server
def serveCustomer(customer):
    customer.createStub()
    customer.executeEvents()
    output = customer.output()
    output_file = open("output.txt", "a")
    output_file.write(str(output) + "\n")
    output_file.close()


# Parse input JSON data and execute processes
def createProcesses(processes):
    customers = []
    customerProcesses = []
    branches = []
    branchIds = []
    branchProcesses = []

    # Create branches
    for process in processes:
        if process["type"] == "branch":
            branch = Branch(process["id"], process["balance"], branchIds)
            branches.append(branch)
            branchIds.append(branch.id)

    # Execute branch processes
    for branch in branches:
        branch_process = multiprocessing.Process(
            target=serveBranch, args=(branch,)
        )
        branchProcesses.append(branch_process)
        branch_process.start()

    sleep(1)

    # Create customers
    for process in processes:
        if process["type"] == "customer":
            customer = Customer(process["id"], process["events"])
            customers.append(customer)

    # Execute customer processes
    for customer in customers:
        customer_process = multiprocessing.Process(
            target=serveCustomer, args=(customer,)
        )
        customerProcesses.append(customer_process)
        customer_process.start()

    # Wait for customer processes to complete
    for customerProcess in customerProcesses:
        customerProcess.join()

    # Terminate branch processes
    for branchProcess in branchProcesses:
        branchProcess.terminate()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file")
    args = parser.parse_args()

    try:
        input = json.load(open(args.input_file))
        open("output.txt", "w").close()
        createProcesses(input)
    except FileNotFoundError:
        print(
            colored(
                "Input file unavailable: '" + args.input_file + "'", "red"
            )
        )
    except json.decoder.JSONDecodeError:
        print(colored("Error decoding JSON file", "red"))
