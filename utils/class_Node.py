#!/usr/bin/env python3

from node_status import status
from subprocess import Popen, call
import sys

class Node():
    node_status = status.IDLE;
    process = '';

    def __init__(self, target):
        self.user = target[0];
        self.ip = target[1];
        self.node_status = status(2);

    def server_up(self):
        self.node_status = status(0);
        self.process = Popen("ssh "+self.user+"@"+self.ip+" './bench/server/bench'", shell=True);

    def client_up(self, server):
        self.node_status = status(1);
        self.process = Popen("ssh "+self.user+"@"+self.ip+" './bench/client/bench "+server+"'", shell=True);

    # this is highly dependent on OS because of the path used
    def distribute_sw(self):
        # with open("log.txt", "w") as outfile:
        print("interacting with: "+self.ip)
        if(call("ssh "+self.user+"@"+self.ip+" 'mkdir bench bench/server bench/server/build bench/server/inc bench/server/log bench/server/src bench/client bench/client/build bench/client/inc bench/client/log bench/client/src'", shell=True)!=0):
            print("remote makedir failed..")
        if(call("scp -r ../bench/server/src "+self.user+"@"+self.ip+":~/bench/server", shell=True)!=0):
            print("secure copy failed..")
        if(call("scp -r ../bench/server/inc "+self.user+"@"+self.ip+":~/bench/server", shell=True)!=0):
            print("secure copy failed..")
        if(call("scp -r ../bench/server/log "+self.user+"@"+self.ip+":~/bench/server", shell=True)!=0):
            print("secure copy failed..")
        if(call("scp -r ../bench/client/inc "+self.user+"@"+self.ip+":~/bench/client", shell=True)!=0):
            print("secure copy failed..")
        if(call("scp -r ../bench/client/src "+self.user+"@"+self.ip+":~/bench/client", shell=True)!=0):
            print("secure copy failed..")
        if(call("scp ../bench/compile "+self.user+"@"+self.ip+":~/bench", shell=True)!=0):
            print("secure copy failed..")
        if(call("scp ../bench/client/CMakeLists.txt "+self.user+"@"+self.ip+":~/bench/client", shell=True)!=0):
            print("secure copy failed..")
        if(call("scp ../bench/server/CMakeLists.txt "+self.user+"@"+self.ip+":~/bench/server", shell=True)!=0):
            print("secure copy failed..")
        if(call("ssh "+self.user+"@"+self.ip+" 'cd bench; ./compile both'", shell=True)!=0):
            print("remote compilation failed")

    def target(self, trg_server):
        if(trg_server == self.ip):
            self.server_up()
        else:
            self.client_up(trg_server)
