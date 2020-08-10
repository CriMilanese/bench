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
import gui
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
            start_python_server(instance)

        for key in keys:
            target(net.edges, key, net.graph[key])

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

if __name__ == '__main__':
    gui.interface()
