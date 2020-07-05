#!usr/bin/env python3

import os
import sys
import time
import re

sys.path.append('utils');
from class_node import Node
import gui
from interactions import *

def play(net):

    all_host = list(net.graph.keys())
    keys = list(net.graph.keys())
    if not all_host:
        raise ValueError("no servers on the list")
    for host in net.graph.values():
        all_host.extend(host)
    all_host = set(all_host)
    print(all_host)
    for instance in all_host:
        distribute_software(instance)
        start_python_server(instance)

    for key in keys:
        target(key, net.graph[key])

    time.sleep(20)
    for instance in all_host:
        stop_python_server(instance)
        print("\n")



def main(behavior):
    """ because main will never die
        this function behaves as instructed from the input, supplied as an argument
        to the script
    """
    if behavior=="compose" or behavior=="all":
        gui.interface()

    return 0
    # check for correct entry format
    r = re.compile('.+ [0-9]+\.[0-9]+\.[0-9]+\.[0-9]+ - .+ [0-9]+\.[0-9]+\.[0-9]+\.[0-9]+ [0-9]+')
    hosts_list = [];
    nodes = []
    with open("config/hosts") as handle:
        hosts_list = handle.read().split("\n");

    # verify config file string format and add new Node instance
    # TODO: hosts_list contains en empty item because of an extra \n
    # in the config file, shall find a neater way
    for host in hosts_list:
        if not host:
            pass
        elif r.match(host):
            by_space = host.split(" ")
            print(by_space)
            nodes.append(Node(by_space));
            del by_space
        else:
            raise ValueError("[ERROR] host format is incorrect")

    # install app
    if(behavior=="copy" or behavior=="all"):
        for node in nodes:
            node.distribute_sw()
        print("[debug] distribution completed");

    # pdb.set_trace()
    # communicate to each host its role
    # make sure each plays the server once
    if(behavior=="all" or behavior=="play"):
        for node in nodes:
            for host in nodes:
                host.target(node.ip)
    elif(behavior=="test_play"):
        for host in nodes:
            if(host.ip=="192.168.1.147"):
                host.target("192.168.1.143")
                print("[DEBUG master] response from the client: "+str(host.resp.bandwidth)+" KB/s")

if __name__ == '__main__':
    if(len(sys.argv) > 1):
        try:
            main(sys.argv[1])
        except ValueError as e:
            print(e)
    else:
        print("missing argument")
