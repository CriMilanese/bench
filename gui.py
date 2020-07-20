"""
	This script handles the GUI, builds a structured representation of the
	network and its hosts as the user inserts them, does some error checking
	and calls back the master to deal with the communications.
"""

import tkinter as tk
import time
import master
from sys import exit, path
path.append("utils")
from class_node import Node
from class_network import Network
from globals import *
from interactions import *

def clear_entry(event):
	background = event.widget.config()['background'][-1];
	if(background==ERROR_COLOR):
		event.widget.delete(0, "end")
		event.widget.config(bg=WHITE)
	feedback.config(text="", fg=ERROR_COLOR);

def check_entries():
	for i, entry in enumerate(frame.entries):
		if i==0 or i==5:
			if entry.get().isalnum():
				pass
			else:
				frame.entries[i].config(bg=ERROR_COLOR)
				raise ValueError("user must be alphanumeric")
		elif i==(len(frame.entries)-1):
			if not entry.get().isdigit():
				frame.entries[i].config(bg=ERROR_COLOR)
				raise ValueError("duration should be a positive digit")
		else:
			if entry.get().isdigit():
				pass
			else:
				frame.entries[i].config(bg=ERROR_COLOR)
				raise ValueError("ip field "+str(i+1)+" type is incorrect")
	return True

def add_node():
	try:
		# prevent click bouncing
		time.sleep(0.2)
		if(check_entries()):
			server_entry = [frame.entries[0].get(), str(frame.entries[1].get()+"."+frame.entries[2].get()+"."+frame.entries[3].get()+"."+frame.entries[4].get()), 0]
			client_entry = [frame.entries[5].get(), str(frame.entries[6].get()+"."+frame.entries[7].get()+"."+frame.entries[8].get()+"."+frame.entries[9].get()), frame.entries[10].get()]
			global network
			network.add_connection(server_entry, client_entry);

	except ValueError as err:
		feedback.config(text=err)

def remove_node():
	try:
		# prevents click bounces
		time.sleep(0.2)
		network.remove_connection()

	except ValueError as err:
		feedback.config(text=err)

def alert(err):
	feedback.config(text=err, fg=ERROR_COLOR)

def draw_buttons():
    global frame
    btn = tk.Button(frame, fg=WHITE, bg=BLUE, text="Test", command= lambda: master.play(network))
    btn.place(relx=0.84, rely=0.95, relwidth=0.16, relheight=0.05)
    btn = tk.Button(frame, fg=WHITE, bg=BLUE, text="Copy Sw", command= lambda: master.copy(network))
    btn.place(relx=0.84, rely=0.87, relwidth=0.16, relheight=0.05)
    btn = tk.Button(frame, fg=WHITE, bg=BLUE, text="Add", command=add_node)
    btn.place(relx=0.75, rely=0.30, relwidth=0.15, relheight=0.05)
    btn = tk.Button(frame, fg=WHITE, bg=BLUE, text="Delete", command=remove_node)
    btn.place(relx=0.75, rely=0.37, relwidth=0.15, relheight=0.05)

# debugging fill up
def fill_entries():
	frame.entries[0].insert(0, "cris")
	frame.entries[1].insert(0, "192")
	frame.entries[2].insert(0, "168")
	frame.entries[3].insert(0, "1")
	frame.entries[4].insert(0, "143")
	frame.entries[5].insert(0, "pi")
	frame.entries[6].insert(0, "192")
	frame.entries[7].insert(0, "168")
	frame.entries[8].insert(0, "1")
	frame.entries[9].insert(0, "146")

def window():
	global root, input_canvas, output_canvas, frame, feedback
	root = tk.Tk()
	root.title("bench GUI")
	input_canvas = tk.Canvas(root, height=HEIGHT, width=WIDTH, bg=BLUE)
	input_canvas.pack()
	frame = tk.Frame(root, bg=LIGHT_BLUE)
	frame.place(relx=0.1, rely=0.1, relwidth=0.8, relheight=0.8)
	feedback = tk.Label(frame, text="", bg=LIGHT_BLUE, fg=ERROR_COLOR)
	feedback.place(relx=0.1, rely=0.45, relwidth=0.8, relheight=0.1)

def display_info():
	label = tk.Label(frame, text=\
	"insert the data for each connection\n \
	user: to access the remote machine with ssh\n" \
	"ip: local ip address for the host\n" \
	"duration: test timeout for this connection\n" \
	"duplicate entries are not allowed", \
	bg=BLUE, fg=GOLD).place(relx=0.1, rely=0.05, relwidth=0.8, relheight=0.15)
	label = tk.Label(frame, text=\
						"user\n--------", \
	bg=LIGHT_BLUE, fg=GOLD).place(relx=0.13, rely=0.23, relwidth=0.1, relheight=0.05)
	label = tk.Label(frame, text=\
						"ip address\n-----------------------------------------------", \
	bg=LIGHT_BLUE, fg=GOLD).place(relx=0.23, rely=0.23, relwidth=0.4, relheight=0.05)
	label = tk.Label(frame, text=\
						"duration\n--------", \
	bg=LIGHT_BLUE, fg=GOLD).place(relx=0.63, rely=0.23, relwidth=0.1, relheight=0.05)
	label = tk.Label(frame, text=\
						"SERVER", \
	bg=LIGHT_BLUE, fg=GOLD).place(relx=0.02, rely=0.29, relwidth=0.1, relheight=0.05)
	label = tk.Label(frame, text=\
						"CLIENT", \
	bg=LIGHT_BLUE, fg=GOLD).place(relx=0.02, rely=0.39, relwidth=0.1, relheight=0.05)

def insert_entries():
	display_info()
	for j in range(int(2)):
		for i in range(int(4)):
			if i == 0:
				dot = tk.Label(frame, text="@", bg=LIGHT_BLUE, fg=GOLD)
			else:
				dot = tk.Label(frame, text=".", bg=LIGHT_BLUE, fg=GOLD)
			dot.place(relx=(0.22+(i*0.1)), rely=0.31+(0.08*j), relwidth=0.02, relheight=0.05)
	frame.entries = []
	for j in range(int(2)):
		for i in range(int(5)):
			entry = tk.Entry(frame, bg=WHITE, justify="center")
			entry.place(relx=0.15+i*0.1, rely=0.30+(0.08*j), relwidth=0.06, relheight=0.05)
			# # ----------- DEBUG --------------
			# entry.insert(0, str((j+1)*(i+1)))
			# # ----------- DEBUG --------------
			entry.focus_set()
			entry.bind("<Button-1>", clear_entry)
			entry.bind("<KeyPress>", clear_entry)
			frame.entries.append(entry)

	# ----------- DEBUG --------------
	fill_entries()
	# ----------- DEBUG --------------

	# this part is for the duration entry, which is not aligned with the others
	entry = tk.Entry(frame, bg=WHITE, justify="center")
	entry.place(relx=0.65, rely=0.33, relwidth=0.06, relheight=0.05)
	# ----------- DEBUG --------------
	entry.insert(0, "10")
	# ----------- DEBUG --------------
	entry.focus_set()
	entry.bind("<Button-1>", clear_entry)
	frame.entries.append(entry)

def interface():
	global network, frame, root
	try:
		window()
		insert_entries()
		network = Network(frame)
		draw_buttons()
		root.mainloop()
	except KeyboardInterrupt:
		root.destroy()
		exit(0)
	except ValueError as e:
		feedback.config(text=e, color=ERROR_COLOR)


if __name__ == "__main__":
	interface()
