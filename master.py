#!usr/bin/env python3
"""
    this script is the starting point of the program,
    it manages the operations on the hosts, abstracted from the user actions
    on the gui.
    # TODO: make the gui a separated process and manage the actions asynchronously

"""

import os
import sys
sys.path.append('utils');
import time
import re
from class_node import Node
import gui
from globals import *
from interactions import *

def play(net):
    try:
        all_host = list(net.graph.keys())
        keys = list(net.graph.keys())
        if not all_host:
            raise ValueError("no servers on the list")
        for host in net.graph.values():
            all_host.extend(host)
        all_host = set(all_host)
        # print(all_host)
        for instance in all_host:
            distribute_software(instance)
            start_python_server(instance)

        for key in keys:
            target(key, net.graph[key])

        time.sleep(20)
        for instance in all_host:
            stop_python_server(instance)
    except ValueError as err:
        gui.alert(err)

def copy(net):
    """
        this function copies the necessary files over to all the hosts
        inserted by the user so far.
    """
    try:
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
    except ValueError as err:
        gui.alert(err)


def main(behavior):
    """
        because main will never die
        this function behaves as instructed from the input, discriminating
        on the basis of the argument given to the script
    """
    if behavior=="compose" or behavior=="all":
        gui.interface()

    return 0

if __name__ == '__main__':
    if(len(sys.argv) > 1):
        try:
            main(sys.argv[1])
        except ValueError as e:
            gui.alert(e)
    else:
        print("missing argument")
