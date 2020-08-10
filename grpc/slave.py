import grpc
from concurrent import futures
import time
import sys
sys.path.append('../utils');
from signal import signal, SIGINT, SIGTERM

#import classes for c library
from ctypes import *
from subprocess import call

# import classes for grpc server
import engage_pb2
import engage_pb2_grpc

# create a class to define the server functions, derived from
# engage_pb2_grpc.engageServicer
class EngageServer(engage_pb2_grpc.TestServicer):

    def terminal(self, lifetime, target):
        result = ''
        if target:
            lib = CDLL("../client/liblclient.so")
            lib.start.argtypes = [c_char_p, c_int]
            lib.start.restype = c_double
            target = c_char_p(target.encode('utf-8'))
            result = lib.start(target, lifetime)
        else:
            result = call("../server/server", shell=True)
        return result

    def Engage(self, request, context):
        metadata = dict(context.invocation_metadata())
        res = self.terminal(request.lifetime, request.target)
        metrics = engage_pb2.Metrics(bandwidth=res)
        return metrics

# create a gRPC server passing a filled thread pool to handle incoming requests
server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))

# use the generated function `add_engageServicer_to_server`
# to add the defined class to the server
engage_pb2_grpc.add_TestServicer_to_server(
        EngageServer(), server)

# listen on port 50051
with open("log", 'w') as log:
    log.write('Slave ready to receive instructions. Listening on port 50051.')
server.add_insecure_port('[::]:50051')
server.start()

def closing(*args):
    server.stop(0)
    sys.exit(0)

signal(SIGINT, closing)
signal(SIGTERM, closing)

# since server.start() will not block,
# a sleep-loop is added to keep alive
try:
    while True:
        time.sleep(5)
except KeyboardInterrupt:
    server.stop(0)
