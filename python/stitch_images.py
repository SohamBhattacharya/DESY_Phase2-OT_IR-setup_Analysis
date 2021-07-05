import argparse
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

import colors
import constants
import BlittedCursor
import GeometryInfo
import ImageInfo


def main() :
    
    # Argument parser
    parser = argparse.ArgumentParser(formatter_class = argparse.RawTextHelpFormatter)
    
    parser.add_argument(
        "--inputDir",
        help = "Location of the input files",
        type = str,
        required = True,
    )
    
    parser.add_argument(
        "--inputPattern",
        help = "Input file name pattern (use XXX and YYY as the coordinate placeholders): image_XXX_YYY.asc",
        type = str,
        required = False,
        default = "cfoam_m20deg_lampoff_XXX_YYY.asc",
    )
    
    parser.add_argument(
        "--inputExt",
        help = "Input file extension",
        type = str,
        required = False,
        default = ".asc",
    )
    
    parser.add_argument(
        "--inputEncoding",
        help = "Input file encoding",
        type = str,
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
        "--ringOpt",
        help = "Ring option",
        type = str,
        required = False,
        default = "odd",
        choices = [constants.odd_str, constants.even_str],
    )
    
    
    args = parser.parse_args()
    d_args = vars(args)
    
    
    tkroot = tkinter.Tk()
    tkroot.wm_title("Main")
    #tkroot.bind('<Control-c>', tkroot.quit)
    tkroot.iconphoto(True, tkinter.PhotoImage(file = "data/dee_icon.png"))
    #self.tk.call('wm', 'iconphoto', self._w, self.icon)
    
    
    imgInfo = ImageInfo.ImageInfo(
        args = args
    )
    imgInfo.draw()
    
    
    geomInfo = GeometryInfo.GeometryInfo(
        args = args,
        imgInfo = imgInfo
    )
    
    
    
    #matplotlib.pyplot.show()
    tkroot.mainloop()
    
    
    return 0


if (__name__ == "__main__") :
    
    main()
