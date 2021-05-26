from tkinter import Canvas
from class_node import Node
from class_edge import Edge, create_hash
from globals import *

class Network():
    # .........
    def __init__(self, container):
        self.hosts = []
        self.edges = {}
        self.graph = {}
        self.servers_history = []
        self.GUI(container)

    def GUI(self, container):
        """
            initiates drawable Canvas where all the geometry is displayed
        """
        self.canvas = Canvas(container, height = CANVAS_HEIGHT, width=CANVAS_WIDTH, bg = LIGHT_BLUE)
        self.canvas.place(relx=0, rely=0.45, relwidth=1, relheight=0.5)

    def pop_edge(self, anchor, server, client):
        """
            deletes the sketch of the edge from the canvas and its data
            representation from the virtual structure, it requires the server
            and client to retrieve the correct line, as each device could have
            more than one connection
        """
        link = create_hash(client, server)
        if link not in self.edges.keys():
            print("not in list")
            return
        self.canvas.delete(self.edges[link].body)
        self.edges[link].label.destroy()
        del self.edges[link]

    def pop_host(self):
        """
            deletes the sketch of the node from the canvas and its data
            representation from the virtual structure
        """
        if not self.hosts:
            raise ValueError("no hosts are present")
        last_host = self.hosts[len(self.hosts)-1]
        if isinstance(last_host, Node):
            self.canvas.delete(last_host.label)
            self.canvas.delete(last_host.body)
            self.hosts.pop()
            self.pop_edge()

    def add_edge(self, source, dest, lifetime):
        """
            draws a line between the nodes coordinates and append its instance
            to a global dictionary with a unique identifier given by the hash
            values of the terminals, relative to the order in which they are
            provided
        """
        link = create_hash(source, dest)
        self.edges[link] = Edge(source, dest, lifetime)
        self.edges[link].show(self.canvas, source, dest)

    def add_connection(self, server, client, lf):
        """
            handles both data storage and data visualization,
            checks whether the network dictionary already contains server and/or
            client signature(s), creating new instances accordingly
        """
        new_server = Node(server[0], server[1])
        new_client = Node(client[0], client[1])
        tmp_values = []
        for x in self.graph.values():
            tmp_values.extend(x)

        tmp_values = set(tmp_values)

        for key in tmp_values:
            if key == new_server:
                new_server = key
            elif key == new_client:
                key = new_client

        # there is a redundant check here, but this remove cycles exploiting hashes
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
        self.add_edge(new_client, new_server, lf)

        # keep track of events in order to delete them
        self.servers_history.append(new_server)

    def remove_connection(self):
        """
            it follows the server history to delete the last connection added,
            this might sound redundant but in Python variable names acts like
            pointers to the same object in memory, hence there is little overhead
            to assignment the same object more than once
        """
        if len(self.servers_history)<=0:
            raise ValueError("No more entries to delete")

        # flatten values of graph dict
        tmp_values = []
        for x in self.graph.values():
            tmp_values.extend(x)

        tmp = self.graph[self.servers_history[-1]]
        print(tmp)
        last = tmp[-1]
        if tmp_values.count(last) == 1:
            self.canvas.delete(last.body)
            self.canvas.delete(last.label)
        if len(tmp)==1:
            lonely = None
            # deletes its symbol only if it does not have any other connection
            for key in self.graph.keys():
                if key == self.servers_history[-1]:
                    self.canvas.delete(key.body)
                    self.canvas.delete(key.label)
                    lonely = key
            if lonely.ip:
                del self.graph[lonely]
            del lonely
        tmp.pop()
        self.pop_edge(self.canvas, self.servers_history.pop(), last)
        del tmp
