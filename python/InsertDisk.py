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


class InsertDisk :
    
    def __init__(
        self,
        r, c,
        radius,
        shape = None,
        dRow = 0,
        dCol = 0,
        offsetRow = 0,
        offsetCol = 0,
    ) :
        
        self.r = r
        self.c = c
        self.radius = radius
        
        self.shape = shape
        
        self.offsetRow = offsetRow
        self.offsetCol = offsetCol
        
        self.dRow_sum = 0
        self.dCol_sum = 0
        
        self.rr, self.cc = self.setAndGetDisk(
            dRow = dRow,
            dCol = dCol,
        )
    
    
    
    def setAndGetDisk(
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
        #    (self.r, self.c),
        #    (self.dRow_sum, self.dCol_sum),
        #    (self.offsetRow, self.offsetCol),
        #    (self.r + self.dRow_sum + self.offsetRow, self.c + self.dCol_sum + self.offsetCol),
        #    self.radius,
        #    self.shape,
        #)
        
        self.rr, self.cc = skimage.draw.disk(
            center = (self.r + self.dRow_sum + self.offsetRow, self.c + self.dCol_sum + self.offsetCol),
            radius = self.radius,
            shape = self.shape,
        )
        
        return (self.rr, self.cc)
