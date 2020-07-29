"""
    the class describing a single connection between two hosts
"""
from tkinter import LAST, Label, StringVar
from globals import WHITE, LIGHT_BLUE
class Edge():

    def __init__(self, lf):
        self.lifetime = lf

    # pass two instances of node to draw a line in between
    def show(self, anchor, a, b):
        self.body = anchor.create_line(a.x, a.y, b.x, b.y, arrow=LAST)
        self.result = StringVar()
        self.label = Label(anchor, textvariable=self.result, fg=WHITE, bg=LIGHT_BLUE)
        self.middle = ((a.x+b.x)/2, (a.y+b.y)/2)
        self.label.place(x=self.middle[0], y=self.middle[1])

    def outcome(self, caller):
        self.result.set(caller.result())

    @staticmethod
    def create_hash(a, b):
        """
            concatenate the strings allows for unique connections given
            the direction of the communication.
        """
        return hash(str(hash(a)).join(str(hash(b))))
