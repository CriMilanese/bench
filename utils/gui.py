# import Host
import tkinter as tk
import sys
import time

HEIGHT = 800
WIDTH = 800
WHITE = '#f4f6ff'
LIGHT_BLUE = '#127681'
BLUE = '#10375c'
GOLD = '#f3c623'
root = ''
canvas = ''
frame = []
feedback = ''

def clear_entry(event):
	event.widget.delete(0, "end")
	event.widget.config(bg=WHITE)
	global feedback
	feedback.config(text="", fg='red');

def move_on():
	global root
	root.destroy()

def check_entries():
	for i, entry in enumerate(frame.entries):
		if i==0 or i==5:
			if entry.get().isalnum():
				pass
			else:
				frame.entries[i].config(bg='red')
				raise ValueError("user must be alphanumeric")
		elif i==(len(frame.entries)-1):
			if entry.get().isdigit():
				pass
			else:
				frame.entries[i].config(bg='red')
				raise ValueError("duration type is incorrect")
		else:
			if entry.get().isdigit():
				pass
			else:
				frame.entries[i].config(bg='red')
				raise ValueError("ip field "+str(i)+" type is incorrect")
	return True


def create_file():
	""" get info from the input fields and construct the configuration
	file to perform the tests requested """
	try:
		if(check_entries()):
				feedback.config(text="new host correctly registered", fg=BLUE)
				with open("config/hosts", "a+") as fd:
					for i, entry in enumerate(frame.entries):
						if i==0 or i==5 or i==(len(frame.entries)-2):
							fd.write(entry.get()+" ")
						elif i==4:
							fd.write(entry.get()+" - ")
						elif i==(len(frame.entries)-1):
							fd.write(entry.get())
						else:
							fd.write(entry.get()+".")
					fd.write("\n")
	except ValueError as err:
		feedback.config(text=err)

def window():
	global root
	root = tk.Tk()
	root.title("bench GUI")
	global canvas
	canvas = tk.Canvas(root, height=HEIGHT, width=WIDTH, bg=BLUE)
	canvas.pack()
	global frame
	frame = tk.Frame(root, bg=LIGHT_BLUE)
	frame.place(relx=0.1, rely=0.1, relwidth=0.8, relheight=0.8)
	global feedback
	feedback = tk.Label(frame, text="", bg=LIGHT_BLUE, fg='red')
	feedback.place(relx=0.1, rely=0.55, relwidth=0.8, relheight=0.1)

def display_info():
	label = tk.Label(frame, text=\
	"insert the data for each connection\nuser: to access the remote machine with ssh\n" \
	"ip: local ip address for the host\n" \
	"duration: test timeout for this node\n", \
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

def insert_host():
	frame.button = tk.Button(frame, fg=WHITE, bg=BLUE, text="Submit", command=create_file)
	frame.button.place(relx=0.75, rely=0.33, relwidth=0.16, relheight=0.05)
	frame.button = tk.Button(frame, fg=WHITE, bg=BLUE, text="Done", command=move_on)
	frame.button.place(relx=0.75, rely=0.4, relwidth=0.16, relheight=0.05)
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
			entry.focus_set()
			entry.bind("<Button-1>", clear_entry)
			frame.entries.append(entry)
	entry = tk.Entry(frame, bg=WHITE, justify="center")
	entry.place(relx=0.65, rely=0.33, relwidth=0.06, relheight=0.05)
	entry.focus_set()
	entry.bind("<Button-1>", clear_entry)
	frame.entries.append(entry)

def interface():
	try:
		window()
		insert_host()
		root.mainloop()
	except KeyboardInterrupt:
		root.destroy();
		sys.exit(0)

if __name__ == "__main__":
	interface();
