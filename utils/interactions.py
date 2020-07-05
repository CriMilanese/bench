import grpc
# import the generated classes
import engage_pb2
import engage_pb2_grpc
from subprocess import Popen, call, DEVNULL, STDOUT
from time import sleep
import signal

def start_python_server(node):
    """ starts a grpc server on the node and attaches its tty to the node instance
    so that we can terminate the process later on """
    cmd = []
    cmd.append("ssh")
    cmd.append("-t")
    cmd.append(str(node.user+"@"+node.ip))
    cmd.append(str("source ~/py_envs/testing/bin/activate; cd bench/grpc; python3 slave.py"))
    node.py_server=Popen(cmd, close_fds=True)
    print(node.py_server)
    del cmd
    # if(node.py_server!=0):
    #     print("remote python server activation failed")
    print("py_server is up and running")
    sleep(2)
    # print("py_server has now value: "+node.py_server)

def stop_python_server(node):
    # cmd = []
    # cmd.append("ssh")
    # cmd.append(str(node.user+"@"+node.ip))
    # cmd.append("kill $(ps aux | grep '[p]ython3' | awk '{print $1}')")
    # if(call(cmd)<0):
    #     raise ValueError("something bad happened")
    node.py_server.terminate()
    print("ssh connection to python grpc slave is interrupted")

def store_result(calling):
    print(calling.result())

def target(server, target_list):
    server_up(server)
    for client in target_list:
        channel = grpc.insecure_channel(client.ip+':50051')
        stub = engage_pb2_grpc.TestStub(channel)
        instance = engage_pb2.Role(lifetime=int(client.lifetime), target=server.ip);
        call = stub.Engage.future(instance)
        call.add_done_callback(store_result)

def server_up(server):
        channel = grpc.insecure_channel(server.ip+':50051')
        stub = engage_pb2_grpc.TestStub(channel)
        instance = engage_pb2.Role(lifetime=0, target=server.ip);
        call = stub.Engage.future(instance)
        call.add_done_callback(store_result)


# this is highly dependent on OS because of the path used
def distribute_software(node):
    # with open("log.txt", "w") as outfile:
    print("interacting with: "+node.ip)
    if(call("ssh "+node.user+"@"+node.ip+" 'mkdir bench bench/server bench/server/build bench/server/inc bench/server/log bench/server/src bench/grpc bench/utils bench/client bench/client/build bench/client/inc bench/client/log bench/client/src'", shell=True, stderr=STDOUT, stdout=DEVNULL)!=0):
        print("[WARN] remote directories exists already or failed to be created")
    if(call("scp -r ../bench/server/src "+node.user+"@"+node.ip+":~/bench/server", shell=True)!=0):
        print("secure copy failed..")
    if(call("scp -r ../bench/server/inc "+node.user+"@"+node.ip+":~/bench/server", shell=True)!=0):
        print("secure copy failed..")
    if(call("scp -r ../bench/server/log "+node.user+"@"+node.ip+":~/bench/server", shell=True)!=0):
        print("secure copy failed..")
    if(call("scp -r ../bench/client/inc/client.h "+node.user+"@"+node.ip+":~/bench/client/inc", shell=True)!=0):
        print("secure copy failed..")
    if(call("scp -r ../bench/client/src "+node.user+"@"+node.ip+":~/bench/client", shell=True)!=0):
        print("secure copy failed..")
    if(call("scp -r ../bench/client/log "+node.user+"@"+node.ip+":~/bench/client", shell=True)!=0):
        print("secure copy failed..")
    if(call("scp ../bench/client/CMakeLists.txt "+node.user+"@"+node.ip+":~/bench/client", shell=True)!=0):
        print("secure copy failed..")
    if(call("scp ../bench/server/CMakeLists.txt "+node.user+"@"+node.ip+":~/bench/server", shell=True)!=0):
        print("secure copy failed..")
    if(call("scp ../bench/grpc/* "+node.user+"@"+node.ip+":~/bench/grpc", shell=True)!=0):
        print("secure copy failed..")
    if(call("scp ../bench/compile "+node.user+"@"+node.ip+":~/bench", shell=True)!=0):
        print("secure copy failed..")
    if(call("ssh "+node.user+"@"+node.ip+" 'cd bench; ./compile all'", shell=True)!=0):
        print("remote compilation failed")
