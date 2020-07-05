#!/usr/bin/env python3
# from node_status import status
from random import randint
from tkinter import Canvas
from globals import GOLD

class Node():

    def __init__(self, info):
        self.user = info[0];
        self.ip = info[1];
        self.lifetime = info[2];
        self.server_handle = ''

    def show(self, anchor, ind):
        if isinstance(anchor, Canvas):
            self.x = randint(10,590);
            self.y = randint(10,290);
            self.body = anchor.create_oval(self.x, self.y, self.x, self.y, outline="white", width=10);
            self.label = anchor.create_text(self.x+10, self.y, text=str(ind), fill=GOLD)

    def __eq__(self, other):
        if self.ip==other.ip and self.user == other.user:
            return True
        else:
            return False

    def __ne__(self, other):
        if self.ip==other.ip and self.user == other.user:
            return False
        else:
            return True

    def __hash__(self):
        tmp = ''
        for a in self.ip.split('.'):
            tmp += a
        return hash(int(tmp))

    def __str__(self):
        return str(self.user + " - " + self.ip)

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
