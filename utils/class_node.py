"""
    Virtual representation of a device, or rather a single network card. As with
    other classes, this one takes care of both the data structure and its
    visual representation on the main canvas.
"""
from random import randint
from tkinter import Canvas
from globals import GOLD

class Node():

    def __init__(self, username, ip_address):
        self.user = username;
        self.ip = ip_address;
        self.server_handle = ''

    def show(self, anchor, ind):
        """
            depicts the node and its label
        """
        if isinstance(anchor, Canvas):
            self.x = randint(10,590);
            self.y = randint(10,290);
            self.body = anchor.create_oval(self.x, self.y, self.x, self.y, outline="white", width=10);
            self.label = anchor.create_text(self.x+10, self.y, text=str(ind), fill=GOLD)

    def get_result(self, caller):
        """
            callback function only for the node which are given the role of
            server.
            TODO: remove it, the server returns nothing as it does not hold
            any valuable information
        """
        self.result = caller.result()

    def __eq__(self, other):
        if self.ip==other.ip and self.user == other.user:
            return True
        else:
            return False

    def __ne__(self, other):
        if self.ip == other.ip and self.user == other.user:
            return False
        else:
            return True

    def __hash__(self):
        return hash(str(self.user+self.ip))

    def __str__(self):
        return self.user + " - " + self.ip

    def __repr__(self):
        return self.user + " - " + self.ip

    def __copy__(self):
        new = type(self)()
        new.ip = self.ip
        new.user = self.user
        new.lifetime = self.lifetime
        new.x = self.x
        new.y = self.y
        new.body = anchor.create_oval(self.x, self.y, self.x, self.y, outline="white", width=10)
        new.label = anchor.create_text(self.x+10, self.y, text=str(ind), fill=GOLD)
        return new
