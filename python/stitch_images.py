import argparse
import collections
import copy
import gc
import glob
import matplotlib
#matplotlib.use("Agg")
matplotlib.use('TkAgg')
import matplotlib.pyplot
import matplotlib.ticker
import mplcursors
import numpy
import pandas
import PIL
import re
import scipy
import skimage
import skimage.draw
import skimage.measure
import sys
import textwrap
import time
import tkinter
import yaml

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from tkinter import filedialog
from tkinter import font

import colors
import constants
import BlittedCursor
import GeometryInfo
import ImageInfo
import Module2SInfo
import UnitConversion
import utils


def main() :
    
    # Argument parser
    parser = argparse.ArgumentParser(formatter_class = argparse.RawTextHelpFormatter)
    
    parser.add_argument(
        "--inputDir",
        help = "Location of the input files",
        type = str,
        #required = True,
        required = False,
    )
    
    parser.add_argument(
        "--inputPattern",
        help = "Input file name pattern (use XXX and YYY as the coordinate placeholders): image_XXX_YYY.asc",
        type = str,
        #required = True,
        required = False,
        default = "cfoam_m20deg_lampoff_XXX_YYY.asc",
    )
    
    parser.add_argument(
        "--inputEncoding",
        help = "Input file encoding",
        type = str,
        #required = True,
        required = False,
        default = "ISO-8859-1",
    )
    
    parser.add_argument(
        "--nCol",
        help = "Number of columns (the trailing delimeter causes problems, so specify this to avoid that)",
        type = int,
        required = False,
        default = 1024,
    )
    
    parser.add_argument(
        "--geomFile",
        help = "Geometry file",
        type = str,
        required = False,
        default = "geometry_carbonFoam.xlsx",
    )
    
    parser.add_argument(
        "--moduleType",
        help = "Module type",
        type = str,
        required = False,
        choices = [constants.module_PS_str, constants.module_2S_str],
    )
    
    parser.add_argument(
        "--ringOpt",
        help = "Ring option",
        type = str,
        required = False,
        default = "odd",
        choices = [constants.odd_str, constants.even_str],
    )
    
    parser.add_argument(
        "--originX",
        help = "Origin x (pixel position)",
        type = float,
        #required = True,
        required = False,
    )
    
    parser.add_argument(
        "--originY",
        help = "Origin y (pixel position)",
        type = float,
        #required = True,
        required = False,
    )
    
    parser.add_argument(
        "--motorRefX",
        help = "Motor x reference (<motor coordinate> <offset from origin in mm>)",
        type = float,
        nargs = 2,
        required = False,
    )
    
    parser.add_argument(
        "--motorRefY",
        help = "Motor y reference (<motor coordinate> <offset from origin in mm>)",
        type = float,
        nargs = 2,
        required = False,
    )
    
    parser.add_argument(
        "--stepxtomm",
        help = "Conversion factor (can be valid math operations): mm/(motor step x)",
        type = str,
        required = False,
    )
    
    parser.add_argument(
        "--stepytomm",
        help = "Conversion factor (can be valid math operations): mm/(motor step y)",
        type = str,
        required = False,
    )
    
    parser.add_argument(
        "--mmtopix",
        help = "Conversion factor (can be valid math operations): pixel/mm",
        type = str,
        required = False,
    )
    
    parser.add_argument(
        "--loadSave",
        help = "Load save file",
        type = str,
        required = False,
        default = None,
    )
    
    
    args = parser.parse_args()
    d_args = vars(args)
    
    
    d_loadInfo = None
    
    if (args.loadSave is not None) :
        
        loadFileName = args.loadSave
        print("Loading configuration from: %s" %(loadFileName))
        
        with open(loadFileName, "r") as fopen :
            
            d_loadInfo = yaml.load(fopen.read(), Loader = yaml.FullLoader)
            #print("Loaded:", d_loadInfo)
            
            d_args.update(d_loadInfo["args"])
            
            #args = d_args
            
            #print(args.inputDir)
            
            print(d_args)
    
    
    def get_saveInfo() :
        
        #l_save_argsInfo = [
        #    "inputDir",
        #    "inputPattern",
        #    "nCol",
        #    "geomFile",
        #    "ringOpt",
        #    "originX",
        #    "originY",
        #    "motorRefX",
        #    "motorRefY",
        #    "stepxtomm",
        #    "stepytomm",
        #    "mmtopix",
        #]
        
        l_save_argsInfo = list(d_args.keys())
        
        d_save_argsInfo = {key: d_args[key] for key in l_save_argsInfo}
        
        return d_save_argsInfo
    
    
    tkroot = tkinter.Tk(className = "Main")
    tkroot.wm_title("Main")
    #tkroot.bind('<Control-c>', tkroot.quit)
    tkroot.iconphoto(True, tkinter.PhotoImage(file = "data/dee_icon.png"))
    #self.tk.call('wm', 'iconphoto', self._w, self.icon)
    
    
    # For some reason tkinter fonts don't work properly with Anaconda python
    #tkfont = tkinter.font.nametofont("TkDefaultFont")
    #tkfont.configure(
    #    family = "newspaper",
    #    size = 9,
    #    #weight = tkinter.font.BOLD
    #)
    #
    #l_tkfont = []
    #
    #for fontname in tkinter.font.names() :
    #    
    #    l_tkfont.append(tkinter.font.nametofont(fontname))
    #    
    #    l_tkfont[-1].configure(
    #        family = "newspaper",
    #        size = 9,
    #        #weight = tkinter.font.BOLD
    #    )
    #
    #tkroot.option_add("*font", "TkDefaultFont")
    
    
    unitConv = UnitConversion.UnitConversion(args)
    
    
    imgInfo = ImageInfo.ImageInfo(
        args = args,
        unitConv = unitConv,
        loadInfo = d_loadInfo[ImageInfo.ImageInfo.__name__] if (d_loadInfo is not None) else None,
    )
    imgInfo.draw()
    
    
    geomInfo = GeometryInfo.GeometryInfo(
        args = args,
        imgInfo = imgInfo,
        unitConv = unitConv,
        loadInfo = d_loadInfo[GeometryInfo.GeometryInfo.__name__] if (d_loadInfo is not None) else None,
    )
    
    
    fig = matplotlib.figure.Figure([5, 10])
    fig.canvas = FigureCanvasTkAgg(fig, master = tkroot)
    #fig.canvas.grid(row = 0, column = 0, sticky = "nsew")
    
    
    row = 0
    
    
    button = tkinter.Button(master = tkroot, text = "All images", takefocus = 0, command = imgInfo.show_allImages)
    button.grid(row = row, column = 0, sticky = "ew")
    
    button = tkinter.Button(master = tkroot, text = "All C-foams", takefocus = 0, command = imgInfo.show_allCfoams)
    button.grid(row = row, column = 1, sticky = "ew")
    row += 1
    
    
    tkroot.grid_rowconfigure(index = row, minsize = 30)
    row += 1
    
    
    label = tkinter.Label(master = tkroot, text = "Origin <x, y>:")
    label.grid(row = row, column = 0, sticky = "w")
    
    tbox_origin = tkinter.Entry(master = tkroot, width = 20)
    tbox_origin.grid(row = row, column = 1, sticky = "ew")
    row += 1
    
    def get_origin() :
        
        x0, y0 = geomInfo.get_origin()
        
        text = "%0.1f, %0.1f" %(x0, y0)
        tbox_origin.delete(0, tkinter.END)
        tbox_origin.insert(0, text)
    
    
    def set_origin() :
        
        xy = tbox_origin.get().strip()
        
        if (not len(xy)) :
            
            return
        
        xy = utils.clean_string(xy)
        xy = tbox_origin.get().split(",")
        
        x0 = float(xy[0])
        y0 = float(xy[1])
        
        geomInfo.set_origin_and_draw(x0 = x0, y0 = y0)
    
    
    button = tkinter.Button(master = tkroot, text = "Get origin", takefocus = 0, command = get_origin)
    button.grid(row = row, column = 0, sticky = "ew")
    
    button = tkinter.Button(master = tkroot, text = "Set origin", takefocus = 0, command = set_origin)
    button.grid(row = row, column = 1, sticky = "ew")
    #ttk.Separator(tkroot, orient = tkinter.VERTICAL).pack(side = tkinter.LEFT, fill = tkinter.Y, padx = 5, pady = 5)
    row += 1
    
    tkroot.grid_rowconfigure(index = row, minsize = 30)
    row += 1
    
    
    def save_config() :
        
        d_save_argsInfo = get_saveInfo()
        d_save_imgInfo = imgInfo.get_saveInfo()
        d_save_geomInfo = geomInfo.get_saveInfo()
        
        d_save = {}
        #d_save = collections.OrderedDict()
        #d_save = collections.UserDict()
        
        d_save["args"] = d_save_argsInfo
        d_save[type(imgInfo).__name__] = d_save_imgInfo
        d_save[type(geomInfo).__name__] = d_save_geomInfo
        
        yaml_save = yaml.dump(d_save)
        
        #print(yaml_save)
        
        saveFileName = tkinter.filedialog.asksaveasfilename(
            parent = tkroot,
            #multiple = False,
            defaultextension = constants.save_extension, filetypes = [("", "*%s" %(constants.save_extension))],
            title = "Save configuration"
        )
        
        print(saveFileName)
        
        with open(saveFileName, "w") as fopen :
            
            fopen.write(yaml_save)
    
    
    button = tkinter.Button(master = tkroot, text = "Save configuration", takefocus = 0, command = lambda: save_config())
    button.grid(row = row, column = 0, sticky = "ew")
    row += 1
    
    
    #matplotlib.pyplot.show()
    tkroot.mainloop()
    
    
    return 0


if (__name__ == "__main__") :
    
    main()
