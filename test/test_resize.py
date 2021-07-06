from tkinter import *

def resize(canvas, w, h) :
    canvas.configure(width = w, height = h)
    canvas.update()

root = Tk()

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

w = Canvas(root, width=200, height=100, bg = "yellow")
w.grid(sticky=N+S+E+W)

w.create_line(0, 0, 200, 100)
w.create_line(0, 100, 200, 0, fill="red", dash=(4, 4))

w.create_rectangle(50, 25, 150, 75, fill="blue")

w.update()
#w.configure(width = root.winfo_width(), height = root.winfo_height())

#root.bind("<Configure>", lambda e: w.configure(width=root.winfo_width(), height=root.winfo_height()))
#root.bind("<Configure>", lambda e: resize(w, e.width, e.height))

root.mainloop()
