#!usr/bin/env python3

import os
import sys
import time
import re
import numpy as np
import pdb

sys.path.append('utils');
from class_Node import Node

def main(target):
    # check for correct entry format
    r = re.compile('.+ [0-9]+\.[0-9]+\.[0-9]+\.[0-9]+')
    hosts_list = [];
    nodes = []
    with open("config/hosts") as handle:
        hosts_list = handle.read().split("\n");

    # verify config file string format and add new Node instance
    # TODO: hosts_list contains en empty item because of an extra \n
    # in the config file, shall find a neater way
    for host in hosts_list:
        if r.match(host):
            nodes.append(Node(host.split(" ")));

    # install app
    if(target=="copy" or target=="both"):
        for node in nodes:
            node.distribute_sw()
        print("[debug] distribution completed");

    # pdb.set_trace()
    # communicate to each host its role
    # make sure each plays the server once
    if(target=="both" or target=="play"):
        for node in nodes:
            print("server is now: "+node.ip)
            for host in nodes:
                host.target(node.ip)
    # node.listen()



if __name__ == '__main__':
    if(len(sys.argv) > 1):
        main(sys.argv[1])
    else:
        print("missing argument")
