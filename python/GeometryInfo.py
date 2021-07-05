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

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

import colors
import constants
import BlittedCursor
import CarbonFoamInfo
import utils


class GeometryInfo :
    
    def __init__(
        self,
        args,
        imgInfo,
    ) :
        self.imgInfo = imgInfo
        self.axis_imgDee = imgInfo.axis_stitchedDee
        
        self.axis_imgDee.figure.canvas.mpl_connect("pick_event", self.on_pick)
        
        
        # Profile figure
        self.tkroot_profile = tkinter.Toplevel()
        self.tkroot_profile.wm_title("Carbon foam profiles")
        
        self.fig_profile = matplotlib.figure.Figure(figsize = [10, 8])
        self.fig_profile.canvas = FigureCanvasTkAgg(self.fig_profile, master = self.tkroot_profile)
        #self.fig_profile = matplotlib.pyplot.figure("Carbon foam profiles", figsize = [10, 8])
        
        self.axis_profile = self.fig_profile.add_subplot(1, 1, 1)
        
        
        # Buttons
        #self.axis_buttons = self.fig_profile.add_axes([0.05, 0.95, 0.1, 0.03])
        #
        #self.button_clear = matplotlib.widgets.Button(self.axis_buttons, "Clear", color = "white", hovercolor = "lightgrey")
        #self.button_clear.on_clicked(self.clear)
        
        self.tbar_profile = NavigationToolbar2Tk(self.fig_profile.canvas, self.tkroot_profile)
        self.tbar_profile.update()
        self.fig_profile.canvas.get_tk_widget().pack(side = tkinter.TOP, fill = tkinter.BOTH, expand = 1)
        
        
        self.button_show_allImages = tkinter.Button(master = self.tkroot_profile, text = "Clear", command = self.clear)
        self.button_show_allImages.pack(side = tkinter.LEFT)
        
        
        self.marker_profile = BlittedCursor.BlittedCursor_mod1(ax = self.axis_profile)
        
        self.xls_cfoam = pandas.ExcelFile(args.geomFile)
        
        self.dframe_cfoam = self.xls_cfoam.parse(0)
        
        # Clean the headers
        self.dframe_cfoam.rename(columns = lambda x: x.strip(), inplace = True)
        
        # Skip empty lines
        self.dframe_cfoam.dropna(how = "all", inplace = True)
        
        #print(self.dframe_cfoam)
        #print(self.dframe_cfoam.keys())
        
        self.d_cfoam = {
            "ring"      : self.dframe_cfoam["Ring"].to_numpy(),
            "r"         : self.dframe_cfoam["r(mm)"].to_numpy(),
            "phi"       : self.dframe_cfoam["phi(deg)"].to_numpy(),
            "arcL"      : self.dframe_cfoam["meanWidth(mm) (orthoradial)"].to_numpy(),
            "radL"      : self.dframe_cfoam["length(mm) (radial)"].to_numpy(),
        }
        
        nFoam = len(self.d_cfoam["r"])
        
        
        arr_dee_shape = imgInfo.arr_stitchedDeeImg.shape+(4,)
        print(arr_dee_shape)
        
        # (y, x)
        #origin_x0 = int(motor_stepX_to_pix(812 - imgInfo.min_motorX))
        #origin_y0 = int(motor_stepY_to_pix(258527 - imgInfo.min_motorY))
        
        origin_x0 = 3390
        origin_y0 = 320
        
        #origin_x0 = 3824
        #origin_y0 = 335
        
        print("origin_x0, origin_y0:", origin_x0, origin_y0)
        
        self.imgInfo.set_origin(xy = (origin_x0, origin_y0))
        
        
        color = (1, 0, 0, 1)
        
        self.l_cfoamNum = [0]*50
        
        self.l_cfoamLabel = []
        
        self.d_geomObj = {}
        self.imgInfo.set_cfoamInfo(self.d_geomObj)
        
        for idx in range(0, nFoam) :
            
            ring = self.d_cfoam["ring"][idx]
            r = utils.mm_to_pix(self.d_cfoam["r"][idx])
            phi_deg = self.d_cfoam["phi"][idx]
            phi = numpy.pi-numpy.radians(phi_deg)
            arcL = utils.mm_to_pix(self.d_cfoam["arcL"][idx])
            radL = utils.mm_to_pix(self.d_cfoam["radL"][idx])
            
            # Odd/even rings
            if (args.ringOpt == constants.odd_str and not ring%2) :
                
                continue
            
            elif (args.ringOpt == constants.even_str and ring%2) :
                
                continue
            
            if (ring > 10) :
                
                continue
            
            if (numpy.isnan(r)) :
                
                continue
            
            ring = int(ring)
            
            self.l_cfoamNum[ring-1] += 1
            
            rInn = r - radL/2.0
            rOut = r + radL/2.0
            
            #print(rInn, rOut)
            
            #rInn = r
            #rOut = r + radL
            
            #dphi = arcL / r
            #dphi = numpy.radians(18)
            
            dphiInn = 2 * numpy.arcsin(arcL / (2.0*rInn))
            dphiOut = 2 * numpy.arcsin(arcL / (2.0*rOut))
            dphiMid = 2 * numpy.arcsin(arcL / (2.0*r))
            
            phiInn1 = phi - dphiInn/2.0
            phiInn2 = phi + dphiInn/2.0
            
            phiOut1 = phi - dphiOut/2.0
            phiOut2 = phi + dphiOut/2.0
            
            phiMid1 = phi - dphiMid/2.0
            phiMid2 = phi + dphiMid/2.0
            
            #print(ring, numpy.degrees(phi1), numpy.degrees(phi), numpy.degrees(phi2), numpy.degrees(dphi))
            
            color = (not color[0], 0, not color[2], 1)
            
            xInn1 = origin_x0+rInn*numpy.cos(phiInn1)
            yInn1 = origin_y0+rInn*numpy.sin(phiInn1)
            
            xInn2 = origin_x0+rInn*numpy.cos(phiInn2)
            yInn2 = origin_y0+rInn*numpy.sin(phiInn2)
            
            xOut1 = origin_x0+rOut*numpy.cos(phiOut1)
            yOut1 = origin_y0+rOut*numpy.sin(phiOut1)
            
            xOut2 = origin_x0+rOut*numpy.cos(phiOut2)
            yOut2 = origin_y0+rOut*numpy.sin(phiOut2)
            
            xMid1 = origin_x0+r*numpy.cos(phiMid1)
            yMid1 = origin_y0+r*numpy.sin(phiMid1)
            
            xMid2 = origin_x0+r*numpy.cos(phiMid2)
            yMid2 = origin_y0+r*numpy.sin(phiMid2)
            
            #print([xInn1, xInn2, xOut2, xOut1], [yInn1, yInn2, yOut2, yOut1])
            
            
            # C-foam label
            cfoamLabel = "R%d/CF%d" %(ring, self.l_cfoamNum[ring-1])
            self.l_cfoamLabel.append([0.5*(xInn1+xInn2), 0.5*(yInn1+yInn2), cfoamLabel])
            
            
            # Attach image
            nearestImgIdx = imgInfo.get_nearestImageIdx(0.5*(xMid1+xMid2), 0.5*(yMid1+yMid2))
            
            self.d_geomObj[cfoamLabel] = CarbonFoamInfo.CarbonFoamInfo(
                imgInfo = self.imgInfo,
                imgIdx = nearestImgIdx,
                label = cfoamLabel,
                axis_profile = self.axis_profile,
                marker_profile = self.marker_profile,
            )
            
            
            # C-foam box
            cfoamBoxLabel = "%s_box" %(cfoamLabel)
            
            cfoamBox_xx = [xInn1, xInn2, xOut2, xOut1]
            cfoamBox_yy = [yInn1, yInn2, yOut2, yOut1]
            
            #rr, cc = skimage.draw.polygon_perimeter(cfoamBox_yy, cfoamBox_xx, shape = arr_dee_shape)
            
            cfoamBox = numpy.array([[pt[0], pt[1]] for pt in zip(cfoamBox_xx, cfoamBox_yy)])
            cfoamBox = matplotlib.patches.Polygon(cfoamBox, color = color, fill = False, picker = None, label = cfoamBoxLabel, zorder = constants.zorder_geometryMesh)
            self.axis_imgDee.add_patch(cfoamBox)
            
            self.d_geomObj[cfoamLabel].add_geometryArtist(cfoamBox, cfoamBoxLabel)
            
            
            # Longitudinal central profile
            profLabel = "%s_prof" %(cfoamLabel)
            
            profLine = self.axis_imgDee.plot([xMid1, xMid2], [yMid1, yMid2], color = color, linewidth = 1, picker = True, pickradius = 3, label = profLabel, zorder = constants.zorder_geometryMesh)[0]
            
            rr_profLine, cc_profLine = skimage.draw.line(int(numpy.round(yMid2)), int(numpy.round(xMid2)), int(numpy.round(yMid1)), int(numpy.round(xMid1)))
            
            rr_profLine = rr_profLine - imgInfo.l_imgExtent_pixelY[nearestImgIdx][0]
            cc_profLine = cc_profLine - imgInfo.l_imgExtent_pixelX[nearestImgIdx][0]
            
            #for idx in range(0, len(rr_profLine)) :
            #    
            #    if (rr_profLine[idx] < 0 or rr_profLine[idx] >= imgInfo.nRow or cc_profLine[idx] < 0 or cc_profLine[idx] >= imgInfo.nCol) :
            #        
            #        rr_profLine[idx] = 0
            #        cc_profLine[idx] = 0
            
            self.d_geomObj[cfoamLabel].add_geometryArtist(profLine, profLabel)
            
            #self.d_geomObj[cfoamLabel].add_profileLine(rr_profLine, cc_profLine, profLabel)
            self.d_geomObj[cfoamLabel].add_profileLine(
                r1 = numpy.round(yMid2) - imgInfo.l_imgExtent_pixelY[nearestImgIdx][0],
                c1 = numpy.round(xMid2) - imgInfo.l_imgExtent_pixelX[nearestImgIdx][0],
                r2 = numpy.round(yMid1) - imgInfo.l_imgExtent_pixelY[nearestImgIdx][0],
                c2 = numpy.round(xMid1) - imgInfo.l_imgExtent_pixelX[nearestImgIdx][0],
                label = profLabel
            )
            
            
            # C-foam text
            self.axis_imgDee.text(
                0.5*(xInn1+xInn2),
                0.5*(yInn1+yInn2),
                cfoamLabel,
                rotation = 90 - (180-phi_deg),
                size = "small",
                horizontalalignment = "center",
                verticalalignment = "center",
                zorder = constants.zorder_geometryText,
            )
        
        
        #self.axis_imgDee.figure.canvas.draw()
    
    
    def on_pick(self, event) :
        
        artist = event.artist
        
        label = artist.get_label()
        print("Picked:", artist, label)
        
        label = label.split("_")[0]
        
        if (label in self.d_geomObj) :
            
            self.d_geomObj[label].on_pick(event)
    
    
    def clear(self) :
        
        for label in self.d_geomObj :
            
            self.d_geomObj[label].unplot_profiles(axis = self.axis_profile, draw = False)
        
        self.fig_profile.canvas.draw()
    
    
    #def on_button_press(self, event) :
    #    
    #    event_key = str(event.key).lower()
    #    event_button = event.button
    #    
    #    clickX = event.xdata
    #    clickY = event.ydata
    #    
    #    print(event_key, event_button, clickX, clickY)
    #    
    #    if (clickX is None or clickY is None) :
    #        
    #        return
    #    
    #    imgIdx = self.imgInfo.get_nearestImageIdx(clickX, clickY)
    #    
    #    
    #    if (imgIdx >= 0) :
    #        
    #        print("Image:", self.imgInfo.l_inputFileName[imgIdx])
