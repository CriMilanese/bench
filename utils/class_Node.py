#!/usr/bin/env python3

from node_status import status
from subprocess import Popen, call
import sys
import grpc
# import the generated classes
import engage_pb2
import engage_pb2_grpc

class Node():

    def __init__(self, target):
        self.user = target[0];
        self.ip = target[1];
        self.lifetime = target[2];
        self.node_status = status(2);
        print("initiate node with:")
        print("ip: "+self.ip)
        print("user: "+self.user)
        print("lifetime: "+self.lifetime)

    def start_python_server(self):
        cmd = str("ssh "+self.user+"@"+self.ip+" '~/py_envs/testing/bin/activate; cd bench/grpc; python3 slave.py'")
        self.py_server=Popen(cmd)
        if(self.py_server!=0):
            print("remote compilation failed")

    def target(self, trg_server):
        channel = grpc.insecure_channel(self.ip+':50051')
        stub = engage_pb2_grpc.TestStub(channel)
        if(trg_server == self.ip):
            self.server_up(stub)
        else:
            self.client_up(stub, trg_server)

    def server_up(self, stub):
        self.node_status = status(0);
        instance = engage_pb2.Role(lifetime=0, target="");
        self.resp = stub.Engage(instance)

    def client_up(self, stub, server):
        self.node_status = status(1);
        role = engage_pb2.Role(lifetime=int(self.lifetime), target=server)
        self.resp = stub.Engage(role)

    # this is highly dependent on OS because of the path used
    def distribute_software(self):
        # with open("log.txt", "w") as outfile:
        print("interacting with: "+self.ip)
        if(call("ssh "+self.user+"@"+self.ip+" 'mkdir bench bench/server bench/server/build bench/server/inc bench/server/log bench/server/src bench/grpc bench/utils bench/client bench/client/build bench/client/inc bench/client/log bench/client/src'", shell=True)!=0):
            print("[WARN] remote directories exists already or failed to be created")
        if(call("scp -r ../bench/server/src "+self.user+"@"+self.ip+":~/bench/server", shell=True)!=0):
            print("secure copy failed..")
        if(call("scp -r ../bench/server/inc "+self.user+"@"+self.ip+":~/bench/server", shell=True)!=0):
            print("secure copy failed..")
        if(call("scp -r ../bench/server/log "+self.user+"@"+self.ip+":~/bench/server", shell=True)!=0):
            print("secure copy failed..")
        if(call("scp -r ../bench/client/inc/client.h "+self.user+"@"+self.ip+":~/bench/client/inc", shell=True)!=0):
            print("secure copy failed..")
        if(call("scp -r ../bench/client/src "+self.user+"@"+self.ip+":~/bench/client", shell=True)!=0):
            print("secure copy failed..")
        if(call("scp -r ../bench/client/log "+self.user+"@"+self.ip+":~/bench/client", shell=True)!=0):
            print("secure copy failed..")
        if(call("scp ../bench/client/CMakeLists.txt "+self.user+"@"+self.ip+":~/bench/client", shell=True)!=0):
            print("secure copy failed..")
        if(call("scp ../bench/server/CMakeLists.txt "+self.user+"@"+self.ip+":~/bench/server", shell=True)!=0):
            print("secure copy failed..")
        if(call("scp ../bench/grpc/* "+self.user+"@"+self.ip+":~/bench/grpc", shell=True)!=0):
            print("secure copy failed..")
        if(call("scp ../bench/compile "+self.user+"@"+self.ip+":~/bench", shell=True)!=0):
            print("secure copy failed..")
        if(call("ssh "+self.user+"@"+self.ip+" 'cd bench; ./compile all'", shell=True)!=0):
            print("remote compilation failed")
