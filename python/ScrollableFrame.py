#Adapted from: https://blog.teclado.com/tkinter-scrollable-frames/

import tkinter
#import tkinter.ttk


class ScrollableFrame(tkinter.ttk.Frame):
    
    def __init__(
        self,
        container,
        w = 1000,
        h = 800,
        *args,
        **kwargs
    ):
        super().__init__(container, *args, **kwargs)
        self.canvas = tkinter.Canvas(self, width = w, height = h) #, bg = "yellow")
        scrollbarh = tkinter.ttk.Scrollbar(self, orient = "horizontal", command = self.xview)
        scrollbarv = tkinter.ttk.Scrollbar(self, orient = "vertical", command = self.yview)
        self.scrollable_frame = tkinter.ttk.Frame(self.canvas)
        
        self.grid_rowconfigure(0, weight = 1)
        self.grid_columnconfigure(0, weight = 1)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion = self.canvas.bbox("all"),
            )
        )
        
        self.scrollable_frame.grid(row = 0, column = 0, sticky = "nsew")
        self.winid = self.canvas.create_window((0, 0), window = self.scrollable_frame, anchor = "nw")
        
        self.canvas.configure(xscrollcommand = scrollbarh.set)
        self.canvas.configure(yscrollcommand = scrollbarv.set)
        
        self.canvas.grid(row = 0, column = 0, sticky = "nsew")
        scrollbarh.grid(row = 1, column = 0, sticky = "ew")
        scrollbarv.grid(row = 0, column = 1, sticky = "ns")
        
        self.pack(expand = True, fill = tkinter.BOTH)
    
    def xview(self, *args):
        
        if self.canvas.xview() == (0.0, 1.0):
            return
        
        self.canvas.xview(*args)
    
    def yview(self, *args):
        
        if self.canvas.yview() == (0.0, 1.0):
            return
        
        self.canvas.yview(*args)
