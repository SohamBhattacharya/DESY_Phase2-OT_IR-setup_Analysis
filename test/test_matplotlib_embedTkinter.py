import datetime

import tkinter
from tkinter import ttk

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

import numpy as np

import tkscrolledframe


class ResizingCanvas(tkinter.Canvas):
    def __init__(self,parent,**kwargs):
        tkinter.Canvas.__init__(self,parent,**kwargs)
        self.bind("<Configure>", self.on_resize)
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()

    def on_resize(self,event):
        print("Resizing")
        # determine the ratio of old width/height to new width/height
        wscale = float(event.width)/self.width
        hscale = float(event.height)/self.height
        self.width = event.width
        self.height = event.height
        # resize the canvas 
        self.config(width=self.width, height=self.height)
        # rescale all the objects tagged with the "all" tag
        self.scale("all",0,0,wscale,hscale)


# https://blog.teclado.com/tkinter-scrollable-frames/
class ScrollableFrame(ttk.Frame):
    def __init__(self, container, w = 900, h = 400, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = tkinter.Canvas(self, width=w, height=h, bg = "yellow")
        #self.canvas = ResizingCanvas(container, width=850, height=400, highlightthickness=0)
        scrollbarh = ttk.Scrollbar(self, orient="horizontal", command=self.xview)
        scrollbarv = ttk.Scrollbar(self, orient="vertical", command=self.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        #self.rowconfigure(0, weight=1)
        #self.columnconfigure(0, weight=1)

        #self.scrollable_frame.grid_rowconfigure(0, weight=1)
        #self.scrollable_frame.grid_columnconfigure(0, weight=1)

        #self.canvas.grid_rowconfigure(0, weight=1)
        #self.canvas.grid_columnconfigure(0, weight=1)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                #width = e.width, height = e.height,
                scrollregion=self.canvas.bbox("all"),
            )
        )

        #self.bind("<Configure>", lambda e: self.canvas.configure(width = container.winfo_width(), height = container.winfo_height()))
        #self.bind("<Configure>", lambda e: self.canvas.configure(width = e.width, height = e.height))

        self.scrollable_frame.grid(row = 0, column = 0, sticky = "nsew")

        self.winid = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw") #, height=400, width=900)
        
        #self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.itemconfigure(self.winid, width=e.width, height=e.height))
        #self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.itemconfigure(self.winid, width=self.canvas.bbox("all")[2], height=self.canvas.bbox("all")[3]))

        self.canvas.configure(xscrollcommand=scrollbarh.set)
        self.canvas.configure(yscrollcommand=scrollbarv.set)

        #canvas.pack(side="left", fill="both", expand=True)
        #scrollbar.pack(side="right", fill="y")

        self.canvas.grid(row = 0, column = 0, sticky = "nsew")
        scrollbarh.grid(row = 1, column = 0, sticky = "ew")
        scrollbarv.grid(row = 0, column = 1, sticky = "ns")

        #self.canvas.addtag_all("all")
        self.pack(expand = True, fill = tkinter.BOTH)

    def xview(self, *args):
        if self.canvas.xview() == (0.0, 1.0):
            return
        self.canvas.xview(*args)

    def yview(self, *args):
        if self.canvas.yview() == (0.0, 1.0):
            return
        self.canvas.yview(*args)



def resize(event, canvas) :
    #canvas.configure(width = event.width, height = event.height)
    print("Resizing", datetime.datetime.now(), canvas.bbox("all"))
    #canvas.update()


root = tkinter.Tk()
root.wm_title("Embedding in Tk")

#root.columnconfigure(0, weight=1)
#root.rowconfigure(0, weight=1)

#root.bind("<Configure>", resize)
#root.wm_grid(sticky = "nsew")

#root.grid_rowconfigure(0, weight=1)
#root.columnconfigure(0, weight=1)

#frame = tkinter.Frame(root)
scrollframe = ScrollableFrame(root)
frame = scrollframe.scrollable_frame

#scrollframe.bind("<Configure>", lambda e: scrollframe.canvas.configure(width = root.winfo_width(), height = root.winfo_height(), scrollregion=scrollframe.canvas.bbox("all")))
scrollframe.bind("<Configure>", lambda e: resize(e, scrollframe.canvas))

#scrollframe.grid(row = 0, column = 0, sticky = "nsew")
#scrollframe.pack()
#frame.pack()
#frame.rowconfigure("all", weight = 0)
#frame.columnconfigure("all", weight = 0)

fig1 = Figure(figsize=(4, 2), dpi=100)
t = np.arange(0, 3, .01)
fig1.add_subplot(111).plot(t, 2 * np.sin(2 * np.pi * t))

fig2 = Figure(figsize=(4, 2), dpi=100)
t = np.arange(0, 3, .01)
fig2.add_subplot(111).plot(t, 2 * np.tan(2 * np.pi * t))

fig1.canvas = FigureCanvasTkAgg(fig1, master=frame)  # A tk.DrawingArea.
fig1.canvas.draw()
#fig1.canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)
fig1.canvas.get_tk_widget().grid(row = 0, column = 0, padx = 5, pady = 5, sticky = "nsew")

toolbar1 = NavigationToolbar2Tk(fig1.canvas, frame, pack_toolbar=False)
toolbar1.update()
#toolbar1.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)
toolbar1.grid(row = 1, column = 0, sticky = "nsew")

fig2.canvas = FigureCanvasTkAgg(fig2, master=frame)  # A tk.DrawingArea.
fig2.canvas.draw()
#fig2.canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)
fig2.canvas.get_tk_widget().grid(row = 0, column = 1, padx = 5, pady = 5, sticky = "nsew")

toolbar2 = NavigationToolbar2Tk(fig2.canvas, frame, pack_toolbar=False)
toolbar2.update()
#toolbar2.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)
toolbar2.grid(row = 1, column = 1, sticky = "nsew")


def on_key_press(event):
    print("you pressed {}".format(event.key))
    #key_press_handler(event, canvas, toolbar)


fig1.canvas.mpl_connect("key_press_event", on_key_press)


def _quit():
    root.quit()     # stops mainloop
    root.destroy()  # this is necessary on Windows to prevent
                    # Fatal Python Error: PyEval_RestoreThread: NULL tstate


def _click():
    print("Clickity click!")


button = tkinter.Button(master=frame, text="Quit", command=_quit)
#button.pack(side=tkinter.LEFT)
button.grid(row = 5, column = 0, sticky = tkinter.SW)

button = tkinter.Button(master=frame, text="Click", command=_click)
#button.pack(side=tkinter.LEFT)
button.grid(row = 5, column = 1, sticky = tkinter.SW)

#frame = tkinter.Frame(root)
#frame.grid(row = 2, column = 2)
#frame.pack()

#frame.rowconfigure("all", weight = 1)
#frame.columnconfigure("all", weight = 1)

#scrollframe.pack(expand = True, fill = tkinter.BOTH)
#scrollframe.grid(sticky = "nsew")
#scrollframe.grid(row = 5, column = 0, sticky = "nsew")

#root.bind("<Configure>", lambda e: scrollframe.canvas.configure(width = e.width, height = e.height))

tkinter.mainloop()
# If you put root.destroy() here, it will cause an error if the window is
# closed with the window manager.
