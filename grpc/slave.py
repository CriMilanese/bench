from grpc import server
from concurrent import futures
from time import sleep
from sys import path, exit
path.append('../utils');
from signal import signal, SIGINT, SIGTERM
from ctypes import *
from subprocess import call
import engage_pb2
import engage_pb2_grpc

# create a class to define the server functions, derived from
# engage_pb2_grpc.engageServicer
class EngageServer(engage_pb2_grpc.TestServicer):
    """
        extends the class generated from grpc compilation, to include
        the custom functions that will run based on instructions given
        by the master script, in order to execute the corresponding program
    """
    def terminal(self, lifetime, target):
        """
            discriminates on the lifetime value to run either a server or a
            client on this machine
        """
        result = None
        if target:
            lib = CDLL("../client/liblclient.so")
            lib.start.argtypes = [c_char_p, c_int]
            lib.start.restype = c_double
            target = c_char_p(target.encode('utf-8'))
            result = lib.start(target, lifetime)
        else:
            result = call("cd ~/bench/server; ./server", shell=True)
        return result

    def Engage(self, request, context):
        """
            dispatches (?) the requested roles
        """
        metadata = dict(context.invocation_metadata())
        res = self.terminal(request.lifetime, request.target)
        metrics = engage_pb2.Metrics(bandwidth=res)
        return metrics

# create a gRPC server passing a filled thread pool to handle incoming requests
grpc_server = server(futures.ThreadPoolExecutor(max_workers=4))

# use the generated function `add_engageServicer_to_server`
# to add the defined class to the server
engage_pb2_grpc.add_TestServicer_to_server(
        EngageServer(), grpc_server)

# listen on localhost at port 50051
grpc_server.add_insecure_port('[::]:50051')
grpc_server.start()

def closing(*args):
    grpc_server.stop(0)
    exit(0)

signal(SIGINT, closing)
signal(SIGTERM, closing)

# since server.start() will not block,
# a sleep-loop is added to keep alive
try:
    while True:
        sleep(1024)
except KeyboardInterrupt:
    grpc_server.stop(0)
