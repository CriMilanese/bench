"""
    the class describing a single connection between two hosts
"""
from tkinter import LAST, Label, StringVar
from globals import WHITE, LIGHT_BLUE, root
from math import floor

class Edge():

    def __init__(self, source, target, lf):
        self.source = source
        self.dest = target
        self.lifetime = lf
        self.string_result = ''

    def show(self, anchor, a, b):
        """
            pass two instances of node to draw a line in between
            this is for the gui to be able to change the connection label on the fly
            as each client returns the results
        """
        self.body = anchor.create_line(a.x, a.y, b.x, b.y, arrow=LAST)
        self.result = StringVar()
        self.label = Label(anchor, textvariable=self.result, fg=WHITE, bg=LIGHT_BLUE)
        middle = ((a.x+b.x)/2, (a.y+b.y)/2)
        self.label.place(x=middle[0], y=middle[1])

    def outcome(self, caller):
        """
            modify the value of this instance variable will cause the label of
            the edge on the GUI to update with the reported bandwidth for that
            connection
        """
        tmp = caller.result()
        self.result.set(str(floor(tmp.bandwidth))+" B/s")
        self.string_result = str(floor(tmp.bandwidth))+" B/s"
        print(self.string_result)

def create_hash(a, b):
    """
        concatenate the strings allows for unique connections given
        the direction of the communication.
    """
    return hash(str(hash(a)).join(str(hash(b))))
