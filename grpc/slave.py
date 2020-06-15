import grpc
from concurrent import futures
import time
import sys
sys.path.append('../utils');

#import classes for c library
from ctypes import *
from subprocess import call

# import classes fro grpc server
import engage_pb2
import engage_pb2_grpc

# create a class to define the server functions, derived from
# engage_pb2_grpc.engageServicer
class EngageServer(engage_pb2_grpc.TestServicer):

    def terminal(self, lifetime, target):
        result = ''
        if (lifetime!=0):
            print("[DEBUG] calling the client")
            lib = CDLL("../client/liblclient.so")
            lib.start.argtypes = [c_char_p, c_int]
            lib.start.restype = c_float
            print("this is the target from the function perspective: "+target)
            target = c_char_p(target.encode('utf-8'))
            print("this is the lifetime from the function perspective: "+str(lifetime))
            result = lib.start(target, lifetime)
            lib.free_results()
        else:
            print("[DEBUG] calling the server")
            print("this is the target from the function perspective: "+target)
            print("this is the lifetime from the function perspective: "+str(lifetime))
            result = call("../server/server", shell=True)
        return result

    def Engage(self, request, context):
        metadata = dict(context.invocation_metadata())
        print(metadata)
        res = self.terminal(request.lifetime, request.target)
        print("float result: "+str(res))
        metrics = engage_pb2.Metrics(bandwidth=res)
        print("[DEBUG slave] "+str(metrics.bandwidth))
        # return response
        return metrics

# create a gRPC server
server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))

# use the generated function `add_engageServicer_to_server`
# to add the defined class to the server
engage_pb2_grpc.add_TestServicer_to_server(
        EngageServer(), server)

# listen on port 50051
print('Slave ready to receive instructions. Listening on port 50051.')
server.add_insecure_port('[::]:50051')
server.start()

# since server.start() will not block,
# a sleep-loop is added to keep alive
try:
    while True:
        time.sleep(86400)
except KeyboardInterrupt:
    server.stop(0)
