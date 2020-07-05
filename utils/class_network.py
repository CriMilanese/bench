from tkinter import Canvas, X, BOTTOM, LAST
from class_node import Node
from globals import *

class Network():
    # .........
    def __init__(self, frame):
        # super().__init__()
        self.hosts = []
        self.edges = []
        self.graph = {}
        self.last_added = []
        self.servers_history = []
        self.GUI(frame)

    def GUI(self, frame):
        self.canvas = Canvas(frame, height = 300, width=700, bg = LIGHT_BLUE)
        self.canvas.pack(fill=X, side=BOTTOM)

    def pop_edge(self):
        if not self.edges:
            return
        last_edge = self.edges[-1]
        self.canvas.delete(last_edge)
        self.edges.pop()

    def pop_host(self):
        if not self.hosts:
            return
        last_host = self.hosts[len(self.hosts)-1]
        if isinstance(last_host, Node):
            self.canvas.delete(last_host.label)
            self.canvas.delete(last_host.body)
            self.hosts.pop()
            self.pop_edge()

    def add_edge(self, source, dest):
        self.edges.append(self.canvas.create_line(source.x, source.y, dest.x, dest.y, arrow=LAST))

    def add_connection(self, server, client):
        """
            handles both data storage and data visualization
            checks whether the network dictionary already contains server and/or
            client signature(s), creating new instances accordingly
        """
        print("------------------add clicked----------------------")
        new_server = Node(server)
        new_client = Node(client)
        tmp_values = []
        for x in self.graph.values():
            tmp_values.extend(x)
        tmp_values = set(tmp_values)
        if new_server in self.graph:
            for key in self.graph:
                if key == new_server:
                    new_server = key
            if new_client in self.graph[new_server]:
                print(self.graph)
                raise ValueError("connection already created")
        else:
            new_server.show(self.canvas, len(self.edges))
            self.graph[new_server] = []

        if new_client in tmp_values:
            for key in tmp_values:
                if key == new_client:
                    new_client = key
        else:
            new_client.show(self.canvas, len(self.edges)+1)

        # add new client to server key
        tmp = self.graph[new_server]
        tmp.append(new_client)
        self.graph[new_server] = tmp

        # draw connection and keep track of it
        self.add_edge(new_client, new_server)

        # keep track of events in order to delete them
        self.servers_history.append(new_server)

        for event in self.servers_history:
            print("servers history: "+str(event))
        print("debug printing graph")
        print(self.graph)

    def remove_connection(self):
        print("------------------remove clicked----------------------")
        tmp = None

        # flatten values
        tmp_values = []
        for x in self.graph.values():
            tmp_values.extend(x)

        # is there still something to delete?
        if len(self.servers_history)<=0:
            raise ValueError("No more entries to delete")

            # if this is any client
        tmp = self.graph[self.servers_history[-1]]
        last = tmp[-1]
        if tmp_values.count(last) == 1:
            print("this client had no other connections")
            self.canvas.delete(last.body)
            self.canvas.delete(last.label)
        if len(tmp)==1:
            lonely = None
            # delete its symbol only if it does not have any other connections
            for key in self.graph.keys():
                if key == self.servers_history[-1]:
                    self.canvas.delete(key.body)
                    self.canvas.delete(key.label)
                    lonely = key
            if lonely.ip:
                del self.graph[lonely]
            del lonely
        tmp.pop()
        self.servers_history.pop()
        self.pop_edge()
        del tmp
        for event in self.servers_history:
            print("servers history: "+str(event))
        print("debug printing graph")
        print(self.graph)
