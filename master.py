#!usr/bin/env python3

import os
import sys
import time
import re

sys.path.append('utils');
from class_Node import Node
import gui

def main(behavior):
    """ because main will never die
        this function behaves as passed from the input as an argument
        to the script
    """
    if behavior=="compose" or behavior=="all":
        gui.interface()

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

    return 0
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
