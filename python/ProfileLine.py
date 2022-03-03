import argparse
import copy
import gc
import glob
import matplotlib
#matplotlib.use("Agg")
#matplotlib.use('TkAgg')
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

import colors
import constants


class ProfileLine :
    
    def __init__(
        self,
        r1, c1,
        r2, c2,
        shape = None,
        dRow = 0,
        dCol = 0,
        offsetRow = 0,
        offsetCol = 0,
        color = "black",
    ) :
        
        self.r1 = r1
        self.c1 = c1
        
        self.r2 = r2
        self.c2 = c2
        
        self.shape = shape
        
        self.offsetRow = offsetRow
        self.offsetCol = offsetCol
        
        self.color = color
        
        self.dRow_sum = 0
        self.dCol_sum = 0
        
        self.rr, self.cc = self.setAndGetLine(
            dRow = dRow,
            dCol = dCol,
        )
        
        self.xx = []
        self.yy = []
    
    
    
    def setAndGetLine(
        self,
        dRow = 0,
        dCol = 0,
        offsetRow = None,
        offsetCol = None,
    ) :
        self.offsetRow = self.offsetRow if (offsetRow is None) else offsetRow
        self.offsetCol = self.offsetCol if (offsetCol is None) else offsetCol
        
        self.dRow_sum += dRow
        self.dCol_sum += dCol
        
        #print(
        #    ("r1", self.r1, self.dRow_sum, self.offsetRow),
        #    ("c1", self.c1, self.dCol_sum, self.offsetCol),
        #    ("r2", self.r2, self.dRow_sum, self.offsetRow),
        #    ("c2", self.c2, self.dCol_sum, self.offsetCol),
        #)
        
        self.rr, self.cc = skimage.draw.line(
            int(numpy.round(self.r1 + self.dRow_sum + self.offsetRow)),
            int(numpy.round(self.c1 + self.dCol_sum + self.offsetCol)),
            int(numpy.round(self.r2 + self.dRow_sum + self.offsetRow)),
            int(numpy.round(self.c2 + self.dCol_sum + self.offsetCol)),
            
            #shape = self.shape,
        )
        
        return (self.rr, self.cc)
    
    
    def setProfileTemp(
        self,
        xx,
        yy,
    ) :
        
        self.xx = xx
        self.yy = yy
        
