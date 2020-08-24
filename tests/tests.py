from time import sleep
from sys import path, argv, exit
from os import chdir
chdir('../')
path.append("utils")
from re import compile, match

from globals import *
from interactions import *
from class_node import Node
from class_edge import Edge

# pi3 , laptop , pi2
pi3 = Node("pi", "192.168.1.146")
pc = Node("cris", "192.168.1.148")
pi2 = Node("pi", "192.168.1.147")
win10 = Node("cristiano", "192.168.1.100")
check = compile("[0-9]+ B/s")

def test_one_client(copy):
    edge = Edge(pi2, pc, 5)
    for device in [pi2, pc]:
        if copy:
            distribute_software(device)
        start_python_server(device)

    server_up(pc)
    client_up(pi2, pc, edge)
    while edge.string_result == '':
        print('just polling')
        sleep(0.5)

    print(edge.string_result)
    assert match(check, str(edge.string_result)), "strings don't match"

    for device in [pi2, pc]:
        stop_python_server(device)

def test_one_win(copy):
    edge = Edge(pc, win10, 5)
    for device in [pc, win10]:
        if copy:
            distribute_software(device)
        start_python_server(device)

    server_up(pc)
    client_up(win10, pc, edge)
    while edge.string_result == '':
        print('just polling')
        sleep(0.5)

    print(edge.string_result)
    assert match(check, str(edge.string_result)), "strings don't match"
    for device in [win10, pc]:
        stop_python_server(device)

def test_one_client_external(copy):
    edge = Edge(pi2, pi3, 10)
    for device in [pi2, pi3]:
        if copy:
            distribute_software(device)
        start_python_server(device)

    server_up(pi2)
    client_up(pi2, pi3, edge)
    while edge.string_result == '':
        print('just polling')
        sleep(0.5)

    print(edge.string_result)
    assert match(check, str(edge.string_result)), "strings don't match"

    for device in [pi2, pi3]:
        stop_python_server(device)

def test_two_clients(copy):
    edge0 = Edge(pi2, pc, 5)
    edge1 = Edge(pi3, pc, 10)
    for device in [pi2, pi3, pc]:
        if copy:
            distribute_software(device)
        start_python_server(device)
    server_up(pc)
    client_up(pi2, pc, edge0)
    client_up(pi3, pc, edge1)
    while not edge1.string_result and not edge0.string_result:
        print('just polling')
        sleep(0.5)
    for edge in [edge0, edge1]:
        print(edge.string_result)
        assert match(check, str(edge.string_result)), "strings don't match"

    for device in [pi2, pi3, pc]:
        stop_python_server(device)

def test_two_clients_same_host(copy):
    edge0 = Edge(pi2, pc, 5)
    edge1 = Edge(pi2, pc, 10)
    for device in [pi2, pc]:
        if copy:
            distribute_software(device)
        start_python_server(device)
    server_up(pc)
    client_up(pi2, pc, edge0)
    client_up(pi2, pc, edge1)
    while not edge1.string_result and not edge0.string_result:
        print('just polling')
        sleep(0.5)
    for edge in [edge0, edge1]:
        print(edge0.string_result)
        print(edge1.string_result)
        assert re.match(check, str(edge.string_result)), "strings don't match"
    for device in [pi2, pc]:
        stop_python_server(device)

if __name__ == "__main__":
    try:
        copy = False
        assert len(argv) > 1, "not enough arguments"
        if "-c" in (argv):
            copy = True
        if "1" in argv:
            test_one_client(copy)
        elif "1e" in argv:
            test_one_client_external(copy)
        elif "1w" in argv:
            test_one_win(copy)
        elif "2" in argv:
            test_two_clients(copy)
        elif "3" in argv:
            test_two_clients_same_host(copy)
        else:
            raise AssertionError("wrong argument")
    except AssertionError as e:
        print(e)
        exit(0)
