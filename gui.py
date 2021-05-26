"""
	This script handles the GUI, builds a structured representation of the
	network and its hosts as the user inserts them, does some error checking
	and calls back the master to deal with the communications.
"""

from tkinter import Label, Button, Toplevel, X, Canvas, Tk, Frame, Entry
import master
from class_node import Node
from class_network import Network
from globals import *
from interactions import *

def clear_entry(event):
	"""
		replaces the content of the widget where the event has happened with
		an empty string and restore its original background color
	"""
	background = event.widget.config()['background'][-1];
	if(background==ERROR_COLOR):
		event.widget.delete(0, "end")
		event.widget.config(bg=WHITE)
	feedback.config(text="", fg=ERROR_COLOR);

def check_entries():
	"""
		verify whether each of the entries contains the expected input format,
		else it raises an error
	"""
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
	"""
		upon correct values format, it provides the necessary information to the
		network class, else it displays the raised error to the user.
	"""
	try:
		if(check_entries()):
			server_entry = [frame.entries[0].get(), str(frame.entries[1].get()+"."+frame.entries[2].get()+"."+frame.entries[3].get()+"."+frame.entries[4].get())]
			client_entry = [frame.entries[5].get(), str(frame.entries[6].get()+"."+frame.entries[7].get()+"."+frame.entries[8].get()+"."+frame.entries[9].get())]
			connection_lifetime = frame.entries[10].get()
			network.add_connection(server_entry, client_entry, connection_lifetime);

	except ValueError as err:
		feedback.config(text=err)

def remove_node():
	"""
		simply removes the last nodes involved in a connection, the network class
		will take care of error handling and mutliple connections nodes
	"""
	try:
		network.remove_connection()
	except ValueError as err:
		feedback.config(text=err)

def show_info():
	"""
		provides a secondary window, displaying a more structured format for the
		connections created and their results if the connections were tested
	"""
	win_info = Toplevel(root)
	win_info.title("Connections transcript")
	info = Canvas(win_info, height=WIN_HEIGHT/2, width=WIN_WIDTH/2, bg=BLUE)
	info.pack(fill=X, expand=1)
	global network
	Label(info, text="source", fg=GOLD, bg=BLUE).grid(row=0, column=1, padx=5, pady=5)
	Label(info, text="destination", fg=GOLD, bg=BLUE).grid(row=0, column=2, padx=5, pady=5)
	Label(info, text="lifetime", fg=GOLD, bg=BLUE).grid(row=0, column=3, padx=5, pady=5)
	Label(info, text="bandwidth", fg=GOLD, bg=BLUE).grid(row=0, column=4, padx=5, pady=5)
	for index, edge in enumerate(network.edges):
		Label(info, text=network.edges[edge].source, fg=WHITE, bg=BLUE).grid(row=index+1, column=1, padx=8, pady=8)
		Label(info, text=network.edges[edge].dest, fg=WHITE, bg=BLUE).grid(row=index+1, column=2, padx=8, pady=8)
		Label(info, text=network.edges[edge].lifetime, fg=WHITE, bg=BLUE).grid(row=index+1, column=3, padx=8, pady=8)
		Label(info, text=network.edges[edge].result.get(), fg=WHITE, bg=BLUE).grid(row=index+1, column=4, padx=8, pady=8)


def alert(err):
	"""
		to be called from other scripts
		TODO: global variables are there for a reason
	"""
	feedback.config(text=err, fg=ERROR_COLOR)

def draw_buttons():
    global frame
    btn = Button(frame, fg=WHITE, bg=BLUE, text="Test", command= lambda: master.play(network))
    btn.place(relx=0, rely=0.95, relwidth=0.15, relheight=0.05)
    btn = Button(frame, fg=WHITE, bg=BLUE, text="Copy Sw", command= lambda: master.copy(network))
    btn.place(relx=0.15, rely=0.95, relwidth=0.15, relheight=0.05)
    btn = Button(frame, fg=WHITE, bg=BLUE, text="Info", command=show_info)
    btn.place(relx=0.3, rely=0.95, relwidth=0.15, relheight=0.05)
    btn = Button(frame, fg=WHITE, bg=BLUE, text="Add", command=add_node)
    btn.place(relx=0.75, rely=0.30, relwidth=0.15, relheight=0.05)
    btn = Button(frame, fg=WHITE, bg=BLUE, text="Delete", command=remove_node)
    btn.place(relx=0.75, rely=0.37, relwidth=0.15, relheight=0.05)

def window():
	global root, frame, feedback
	root = Tk()
	root.title("Traffic Ward")
	input_canvas = Canvas(root, height=WIN_HEIGHT, width=WIN_WIDTH, bg=BLUE)
	input_canvas.pack()
	frame = Frame(root, bg=LIGHT_BLUE)
	frame.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.9)
	feedback = Label(frame, text="", bg=LIGHT_BLUE, fg=ERROR_COLOR)
	feedback.place(relx=0.5, rely=0.95, relwidth=0.5, relheight=0.05)

def display_labels():
	label = Label(frame, text=\
	"Welcome!\n" \
	"this tool will help you calculate the maximum bandwidth\n" \
	"available across the devices connected within your local network\n" \
	"----------------------------------------------------------------\n" \
	"in order to proceed, you need ssh passwordless authentication between the hosts", \
	bg=BLUE, fg=GOLD).place(relx=0.1, rely=0.05, relwidth=0.8, relheight=0.15)
	label = Label(frame, text=\
						"user\n--------", \
	bg=LIGHT_BLUE, fg=GOLD).place(relx=0.13, rely=0.23, relwidth=0.1, relheight=0.05)
	label = Label(frame, text=\
						"ip address\n-----------------------------------------------", \
	bg=LIGHT_BLUE, fg=GOLD).place(relx=0.23, rely=0.23, relwidth=0.4, relheight=0.05)
	label = Label(frame, text=\
						"duration\n--------", \
	bg=LIGHT_BLUE, fg=GOLD).place(relx=0.63, rely=0.23, relwidth=0.1, relheight=0.05)
	label = Label(frame, text=\
						"SERVER", \
	bg=LIGHT_BLUE, fg=GOLD).place(relx=0.02, rely=0.3, relwidth=0.1, relheight=0.05)
	label = Label(frame, text=\
						"CLIENT", \
	bg=LIGHT_BLUE, fg=GOLD).place(relx=0.02, rely=0.38, relwidth=0.1, relheight=0.05)

# debugging fill up
def fill_entries():
	frame.entries[0].insert(0, "cris")
	frame.entries[1].insert(0, "192")
	frame.entries[2].insert(0, "168")
	frame.entries[3].insert(0, "1")
	frame.entries[4].insert(0, "148")
	frame.entries[5].insert(0, "pi")
	frame.entries[6].insert(0, "192")
	frame.entries[7].insert(0, "168")
	frame.entries[8].insert(0, "1")
	frame.entries[9].insert(0, "146")

def insert_entries():
	display_labels()
	for j in range(int(2)):
		for i in range(int(4)):
			if i == 0:
				token = Label(frame, text="@", bg=LIGHT_BLUE, fg=GOLD)
			else:
				token = Label(frame, text=".", bg=LIGHT_BLUE, fg=GOLD)
			token.place(relx=(0.22+(i*0.1)), rely=0.3+(0.08*j), relwidth=0.02, relheight=0.05)
	frame.entries = []
	for j in range(int(2)):
		for i in range(int(5)):
			entry = Entry(frame, bg=WHITE, justify="center")
			entry.place(relx=0.15+i*0.1, rely=0.3+(0.08*j), relwidth=0.06, relheight=0.04)
			entry.focus_set()
			entry.bind("<Button-1>", clear_entry)
			entry.bind("<Key>", clear_entry)
			frame.entries.append(entry)

	# ----------- DEBUG --------------
	fill_entries()
	# ----------- DEBUG --------------

	# this part is for the duration entry, which is not aligned with the others
	entry = Entry(frame, bg=WHITE, justify="center")
	entry.place(relx=0.65, rely=0.33, relwidth=0.06, relheight=0.04)
	entry.focus_set()
	entry.bind("<Button-1>", clear_entry)
	entry.bind("<Key>", clear_entry)
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
		return 0
	except ValueError as e:
		feedback.config(text=e, color=ERROR_COLOR)


if __name__ == "__main__":
	interface()
