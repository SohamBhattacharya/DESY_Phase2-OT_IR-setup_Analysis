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
        dRow = 0,
        dCol = 0,
    ) :
        
        self.r1 = r1
        self.c1 = c1
        
        self.r2 = r2
        self.c2 = c2
        
        self.dRow_sum = 0
        self.dCol_sum = 0
        
        self.rr, self.cc = self.setAndGetLine(dRow = dRow, dCol = dCol)
    
    
    
    def setAndGetLine(self, dRow = 0, dCol = 0) :
        
        self.dRow_sum += dRow
        self.dCol_sum += dCol
        
        self.rr, self.cc = skimage.draw.line(
            int(numpy.round(self.r1 + self.dRow_sum)),
            int(numpy.round(self.c1 + self.dCol_sum)),
            int(numpy.round(self.r2 + self.dRow_sum)),
            int(numpy.round(self.c2 + self.dCol_sum))
        )
        
        return (self.rr, self.cc)
