import time
import sys
import re
import subprocess
sys.path.append("utils")

from globals import *
from interactions import *
from class_node import Node
from class_edge import Edge

# pi3 , laptop , pi2
pi3 = Node(["pi", "192.168.1.146"])
pc = Node(["cris", "192.168.1.148"])
pi2 = Node(["pi", "192.168.1.147"])

def test_one_client(copy):
    edge = Edge(pi2, pc, 5)
    check = re.compile("bandwidth: [0-9]+\.[0-9]+")
    for device in [pi2, pc]:
        if copy:
            distribute_software(device)
        start_python_server(device)

    server_up(pc)
    client_up(pi2, pc, edge)
    while edge.result == '':
        print('just polling')
        time.sleep(0.5)
    assert re.match(check, str(edge.result)), "strings don't match"
    print(edge.result)
    for device in [pi2, pc]:
        stop_python_server(device)

def test_one_client_external(copy):
    edge = Edge(pi2, pi3, 10)
    check = re.compile("bandwidth: [0-9]+\.[0-9]+")
    for device in [pi2, pi3]:
        if copy:
            distribute_software(device)
        start_python_server(device)

    server_up(pi2)
    client_up(pi2, pi3, edge)
    while edge.result == '':
        print('just polling')
        time.sleep(0.5)
    assert re.match(check, str(edge.result)), "strings don't match"
    print(edge.result)
    for device in [pi2, pi3]:
        stop_python_server(device)

def test_two_clients(copy):
    edge0 = Edge(pi2, pc, 5)
    edge1 = Edge(pi3, pc, 10)
    check = re.compile("bandwidth: [0-9]+\.[0-9]+")
    for device in [pi2, pi3, pc]:
        if copy:
            distribute_software(device)
        start_python_server(device)
    server_up(pc)
    client_up(pi2, pc, edge0)
    client_up(pi3, pc, edge1)
    while not edge1.result and not edge0.result:
        print('just polling')
        time.sleep(0.5)
    for edge in [edge0, edge1]:
        assert re.match(check, str(edge.result)), "strings don't match"
        print(edge.result)

    for device in [pi2, pi3, pc]:
        stop_python_server(device)

def test_two_clients_same_host(copy):
    edge0 = Edge(pi2, pc, 5)
    edge1 = Edge(pi2, pc, 10)
    check = re.compile("bandwidth: [0-9]+\.[0-9]+")
    for device in [pi2, pc]:
        if copy:
            distribute_software(device)
        start_python_server(device)
    server_up(pc)
    client_up(pi2, pc, edge0)
    client_up(pi2, pc, edge1)
    while not edge1.result and not edge0.result:
        print('just polling')
        time.sleep(0.5)
    for edge in [edge0, edge1]:
        assert re.match(check, str(edge.result)), "strings don't match"
    print(edge0.result)
    print(edge1.result)
    print("python servers were taken down")
    for device in [pi2, pc]:
        stop_python_server(device)

if __name__ == "__main__":
    try:
        copy = False
        assert len(sys.argv) > 1, "not enough arguments"
        if "-c" in (sys.argv):
            copy = True
        if "1" in sys.argv:
            test_one_client(copy)
        elif "1e" in sys.argv:
            test_one_client_external(copy)
        elif "2" in sys.argv:
            test_two_clients(copy)
        elif "3" in sys.argv:
            test_two_clients_same_host(copy)
        else:
            raise AssertionError("wrong argument")
    except AssertionError as e:
        print(e)
        sys.exit(0)
