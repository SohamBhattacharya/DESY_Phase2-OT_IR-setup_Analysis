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
import os
import pandas
import PIL
import re
import scipy
import scipy.fft
import scipy.signal
import skimage
import skimage.draw
import skimage.measure
import sys
import textwrap
import time
import tkinter
import yaml

matplotlib.pyplot.rcParams["text.usetex"] = True
matplotlib.pyplot.rcParams["text.latex.preamble"] = r"\usepackage{amsmath}"

import ROOT
ROOT.gROOT.SetBatch(1)

import constants
import colors
import utils


def main() :
    
    # Argument parser
    parser = argparse.ArgumentParser(formatter_class = argparse.ArgumentDefaultsHelpFormatter)
    
    parser.add_argument(
        "--datayml",
        help = "The yml file with the data",
        type = str,
        required = True,
    )
    
    
    args = parser.parse_args()
    d_args = vars(args)
    
    print("Loading data from: %s" %(args.datayml))
    
    d_coolCircData = {}
    
    with open(args.datayml, "r") as fopen :
        
        d_coolCircData = yaml.load(fopen.read(), Loader = yaml.FullLoader)
    
    #print(d_coolCircData)
    
    pattern_str = "R{ring}/2S{module}_ins{insert}"
    pattern_str_regex = "R(\d+)/2S(\d+)_ins(\d+)"
    
    for circuit in d_coolCircData.keys() :
        
        l_insertLabel = d_coolCircData[circuit]["inserts"]
        
        print(circuit)
        print(l_insertLabel)
        
        l_insertLabel_reflect = []
        circuit_reflect = d_coolCircData[circuit]["reflect"]["transformation"]
        d_reflect_transformation = d_coolCircData[circuit]["reflect"]["transformation"]
        
        for insertLabel in l_insertLabel :
            
            #ring = insertLabel.split("/")[0]
            #
            #module = insertLabel.split("/")[1]
            #
            #insert = module.split("_")[1]
            #insert = insert.split("ins")[1]
            #
            #module = module.split("_")[0]
            #module = module.split("R")[0]
            
            ring, module, insert = re.findall(pattern_str_regex, insertLabel)[0]
            
            d_format = {
                "ring": module,
                "module": module,
                "insert": insert,
            }
            
            #print(d_reflect_transformation)
            
            insertLabel_reflect = pattern_str.format(
                ring = ring,
                module = eval(d_reflect_transformation["module"][ring].format(**d_format)),
                insert = eval(d_reflect_transformation["insert"][insert].format(**d_format))
            )
            
            l_insertLabel_reflect.append(insertLabel_reflect)
            
            #print(insertLabel, ring, module, insert, ll)
            #print(insertLabel, ring, module, insert)
            #print(insertLabel_reflect)
        
        
        print(circuit_reflect)
        print(l_insertLabel_reflect)


if (__name__ == "__main__") :
    
    main()
