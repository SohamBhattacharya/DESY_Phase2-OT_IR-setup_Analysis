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
import yaml


class CoolingCircuit2SInfo :
    
    def __init__(
        self,
        label,
        l_insertLabel,
        d_geomObj,
        axis,
    ) :
        
        self.label = label
        self.l_insertLabel = l_insertLabel
        self.d_geomObj = d_geomObj
        self.axis = axis
        
        self.line = None
        self.l_annotation = None
        
        self.fitParVals = None
        self.fitParErrs = None
        self.fitFunc = lambda x, p0, p1: p0 + p1*x
        #self.fitFuncStr = "{0}+{1}x"
        
        #self.draw()
    
    
    def getTemp(self, insertLabel) :
        
        moduleLabel = insertLabel.split("_")[0]
        minTemp = self.d_geomObj[moduleLabel].get_minTemp(label = insertLabel)
        
        return minTemp
    
    
    def draw(self) :
        
        xx = []
        yy = []
        
        self.l_annotation = []
        
        for insertLabel in self.l_insertLabel :
            
            yy.append(self.getTemp(insertLabel = insertLabel))
        
        xx = list(range(1, len(yy)+1))
        
        self.line, = self.axis.plot(xx, yy, "o--", label = self.label, picker = True, pickradius = 3)
        
        for x, y, label in zip(xx, yy, self.l_insertLabel) :
            
            self.l_annotation.append(self.axis.annotate(
                text = label,
                xy = (x, y),
                #rotation = 45,
                size = "x-small",
                horizontalalignment = "left",
                verticalalignment = "bottom",
                #zorder = constants.zorder_geometryText,
                #annotation_clip = False,
            ))
            
            self.l_annotation[-1].set_visible(False)
        
        self.fit()
        
        self.axis.relim()
        self.axis.autoscale_view()
        
        self.axis.figure.canvas.draw()
    
    
    def update(self, l_insertLabel) :
        
        # Get the list of inserts to be updated
        l_insertLabel = list(set(l_insertLabel).intersection(self.l_insertLabel))
        
        
        if (not len(l_insertLabel)) :
            
            return
        
        ydata = self.line.get_ydata()
        
        for insertLabel in l_insertLabel :
            
            idx = self.l_insertLabel.index(insertLabel)
            
            y = self.getTemp(insertLabel = insertLabel)
            
            ydata[idx] = y
            
            self.l_annotation[idx].set_y(y)
        
        self.line.set_ydata(ydata)
        
        self.fit()
        
        self.axis.relim()
        self.axis.autoscale_view()
        
        self.axis.figure.canvas.draw()
    
    
    def fit(self) :
        
        xdata = self.line.get_xdata()
        ydata = self.line.get_ydata()
        
        popt, pcov = scipy.optimize.curve_fit(f = self.fitFunc, xdata = xdata, ydata = ydata)
        perr = numpy.sqrt(numpy.diag(pcov))
        print("%s:\t\t p0 = %+0.4f±%0.4f, p1 = %+0.4f±%0.4f" %(self.label, popt[0], perr[0], popt[1], perr[1]))
    
    
    #def get_fitStr(self) :
    #    
    #    if (self.fitParVals is None or self.fitParErrs is None) :
    #        
    #        return
    #    
    #    d_pars = 