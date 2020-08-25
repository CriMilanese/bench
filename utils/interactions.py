"""
    This file contains the actions that the tool issues against other devices,
    carried out by the shell through ssh commands and/or through the grpc service
"""

import grpc
import engage_pb2
import engage_pb2_grpc
from subprocess import Popen, call, DEVNULL, STDOUT
from time import sleep
from class_edge import create_hash

def start_python_server(node):
    """
        starts a grpc server on the device and attaches its tty to the node instance
        so that I can terminate it later on
    """
    cmd = []
    cmd.append("ssh")
    cmd.append("-t")
    cmd.append(str(node.user+"@"+node.ip))
    cmd.append(str("source ~/py_envs/testing/bin/activate; cd ~/bench/grpc; python3 slave.py"))
    node.server_handle=Popen(cmd, close_fds=True)
    sleep(2)

def stop_python_server(node):
    """
        exploits the device handle created above to send a terminating signal
        to the process spawned, which in turn terminates the remote one, because
        of the -t argument of the ssh command, which merged the in/out streams
    """
    node.server_handle.terminate()

def target(edges_dict, server, target_list):
    """
        addresses each host with their relative role by opening a channel with
        their running slave, format the request message as per the proto buffer
        standard and sets up a callback function to asychronously retrieve the
        results
    """

    server_up(server)
    for device in target_list:
        link = create_hash(device, server)
        client_up(device, server, edges_dict[link])

def server_up(server):
    """
        tells the host to behave like a server by running the corresponding c
        subroutine, no need to create a link for its returning value as the server
        only acts passively and does not provide useful information back
    """
    channel = grpc.insecure_channel(server.ip+':50051')
    stub = engage_pb2_grpc.TestStub(channel)
    instance = engage_pb2.Role(lifetime=0, target=None);
    call = stub.Engage.future(instance)
    call.add_done_callback(server.get_result)

def client_up(client, targ, edge):
    """
        tells the client to run the c client routine
        targeting the server passed as second parameter, it also ties the
        callback to the edge instance
    """
    channel = grpc.insecure_channel(client.ip+':50051')
    stub = engage_pb2_grpc.TestStub(channel)
    instance = engage_pb2.Role(lifetime=int(edge.lifetime), target=targ.ip);
    call = stub.Engage.future(instance)
    call.add_done_callback(edge.outcome)

def distribute_software(node):
    """
        Provides all hosts with the necessary package of files, suppressing the
        standard file descriptors but checking the returning values.
        This is highly dependent on OS because of the nature and syntax of the
        commands used, the shell attribute loads the remote terminal environmental
        variables, which might compromise the benefits of cmake.
        TODO: consider the security issues due to the use of 'shell=True' and
        eventually refactor.
    """
    if(call("ssh "+node.user+"@"+node.ip+" 'mkdir bench \
                                            bench/server \
                                            bench/server/build \
                                            bench/server/inc \
                                            bench/server/log \
                                            bench/server/src \
                                            bench/grpc \
                                            bench/utils \
                                            bench/client \
                                            bench/client/build \
                                            bench/client/inc \
                                            bench/client/log \
                                            bench/client/src'",
                shell=True, stderr=STDOUT, stdout=DEVNULL) != 0):
        print("[WARN] remote directories exists already or failed to be created")
    if(call("scp -r ../bench/server/src "+node.user+"@"+node.ip+":~/bench/server", shell=True, stderr=STDOUT, stdout=DEVNULL)!=0):
        print("secure copy failed..")
    if(call("scp -r ../bench/server/inc "+node.user+"@"+node.ip+":~/bench/server", shell=True, stderr=STDOUT, stdout=DEVNULL)!=0):
        print("secure copy failed..")
    if(call("scp -r ../bench/server/log "+node.user+"@"+node.ip+":~/bench/server", shell=True, stderr=STDOUT, stdout=DEVNULL)!=0):
        print("secure copy failed..")
    if(call("scp ../bench/client/inc/client.h "+node.user+"@"+node.ip+":~/bench/client/inc", shell=True, stderr=STDOUT, stdout=DEVNULL)!=0):
        print("secure copy failed..")
    if(call("scp -r ../bench/client/src "+node.user+"@"+node.ip+":~/bench/client", shell=True, stderr=STDOUT, stdout=DEVNULL)!=0):
        print("secure copy failed..")
    if(call("scp -r ../bench/client/log "+node.user+"@"+node.ip+":~/bench/client", shell=True, stderr=STDOUT, stdout=DEVNULL)!=0):
        print("secure copy failed..")
    if(call("scp ../bench/client/CMakeLists.txt "+node.user+"@"+node.ip+":~/bench/client", shell=True, stderr=STDOUT, stdout=DEVNULL)!=0):
        print("secure copy failed..")
    if(call("scp ../bench/server/CMakeLists.txt "+node.user+"@"+node.ip+":~/bench/server", shell=True, stderr=STDOUT, stdout=DEVNULL)!=0):
        print("secure copy failed..")
    if(call("scp ../bench/grpc/* "+node.user+"@"+node.ip+":~/bench/grpc", shell=True, stderr=STDOUT, stdout=DEVNULL)!=0):
        print("secure copy failed..")
    if(call("scp ../bench/compile "+node.user+"@"+node.ip+":~/bench", shell=True, stderr=STDOUT, stdout=DEVNULL)!=0):
        print("secure copy failed..")
    if(call("ssh "+node.user+"@"+node.ip+" 'cd bench; ./compile all'", shell=True, stderr=STDOUT, stdout=DEVNULL)!=0):
        print("remote compilation failed")
