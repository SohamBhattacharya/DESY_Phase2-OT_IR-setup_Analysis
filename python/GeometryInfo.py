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
import Module2SInfo
import utils


class GeometryInfo :
    
    def __init__(
        self,
        args,
        imgInfo,
        unitConv,
        loadInfo = None,
    ) :
        self.args = args
        self.imgInfo = imgInfo
        
        self.unitConv = unitConv
        
        self.originVarName_x0 = "origin_x0"
        self.originVarName_y0 = "origin_y0"
        
        #self.origin_x0 = None
        #self.origin_y0 = None
        
        setattr(self, self.originVarName_x0, None)
        setattr(self, self.originVarName_y0, None)
        
        self.loadInfo = loadInfo
        
        if (self.loadInfo is None) :
            
            self.set_origin_and_draw(args.originX, args.originY)
        
        else :
            
            self.set_origin_and_draw(loadInfo[self.originVarName_x0], loadInfo[self.originVarName_y0])
    
    
    def set_origin_and_draw(self, x0, y0) :
        
        #if ((x0, y0) == self.get_origin()) :
        #    
        #    return
        
        self.set_origin(x0, y0)
        self.draw(recreate = True)
    
    
    def set_origin(self, x0, y0) :
        
        self.origin_x0 = x0
        self.origin_y0 = y0
    
    
    def get_origin(self) :
        
        return (self.origin_x0, self.origin_y0)
    
    
    def draw(self, recreate = False) :
        
        if (recreate and hasattr(self, "tkroot_profile")) :
            
            self.tkroot_profile.destroy()
            
            for key in self.d_geomObj :
                
                self.d_geomObj[key].destroy()
            
            gc.collect()
            
            self.imgInfo.draw(recreate = True)
        
        axis_imgDee = self.imgInfo.axis_stitchedDee
        axis_imgDee.figure.canvas.mpl_connect("pick_event", self.on_pick)
        
        # Profile figure
        self.tkroot_profile = tkinter.Toplevel(class_ = "Carbon foam profiles")
        self.tkroot_profile.wm_title("Carbon foam profiles")
        
        self.fig_profile = matplotlib.figure.Figure(figsize = [10, 8])
        self.fig_profile.canvas = FigureCanvasTkAgg(self.fig_profile, master = self.tkroot_profile)
        #self.fig_profile = matplotlib.pyplot.figure("Carbon foam profiles", figsize = [10, 8])
        
        self.fig_profile.canvas.mpl_connect("pick_event", self.on_pick)
        
        self.axis_profile = self.fig_profile.add_subplot(1, 1, 1)
        
        self.axis_profile.set_xlabel("Pixel")
        self.axis_profile.set_ylabel("Temperature [°C]")
        
        
        
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
        
        self.xls_geometry = pandas.ExcelFile(self.args.geomFile)
        
        self.dframe_geometry = self.xls_geometry.parse(0)
        
        # Clean the headers
        self.dframe_geometry.rename(columns = lambda x: x.strip(), inplace = True)
        
        # Skip empty lines
        self.dframe_geometry.dropna(how = "all", inplace = True)
        
        #print(self.dframe_geometry)
        #print(self.dframe_geometry.keys())
        
        self.d_geometry = {
            "ring"             : self.dframe_geometry["Ring"].to_numpy(),
            "r"                : self.dframe_geometry["r(mm)"].to_numpy(),
            "phi"              : self.dframe_geometry["phi(deg)"].to_numpy(),
            "arcL"             : self.dframe_geometry["meanWidth(mm) (orthoradial)"].to_numpy(),
            "radL"             : self.dframe_geometry["length(mm) (radial)"].to_numpy(),
            "insert_outR"      : self.dframe_geometry["insert outer radius (mm)"].to_numpy(),
        }
        
        nModule = len(self.d_geometry["r"])
        
        
        #arr_dee_shape = self.imgInfo.arr_stitchedDeeImg.shape+(4,)
        #print(arr_dee_shape)
        
        # (y, x)
        #self.origin_x0 = int(motor_stepX_to_pix(812 - self.imgInfo.min_motorX))
        #self.origin_y0 = int(motor_stepY_to_pix(258527 - self.imgInfo.min_motorY))
        
        #self.origin_x0 = 3390
        #self.origin_y0 = 320
        
        #self.origin_x0 = 3824
        #self.origin_y0 = 335
        
        print("self.origin_x0, self.origin_y0:", self.origin_x0, self.origin_y0)
        
        self.imgInfo.set_origin(x0 = self.origin_x0, y0 = self.origin_y0)
        
        
        color = (1, 0, 0, 1)
        
        self.l_cfoamNum = [0]*50
        self.l_cfoamLabel = []
        
        self.l_module2SNum = [0]*50
        self.l_module2SLabel = []
        
        self.d_geomObj = {}
        self.imgInfo.set_cfoamInfo(self.d_geomObj)
        
        for idx in range(0, nModule) :
            
            ring = self.d_geometry["ring"][idx]
            r = self.unitConv.mm_to_pix(self.d_geometry["r"][idx])
            phi_deg = self.d_geometry["phi"][idx]
            phi = numpy.pi-numpy.radians(phi_deg)
            arcL = self.unitConv.mm_to_pix(self.d_geometry["arcL"][idx])
            radL = self.unitConv.mm_to_pix(self.d_geometry["radL"][idx])
            
            # Module type (PS/2S)
            if (
                ring < constants.d_moduleDetails[self.args.moduleType][self.args.ringOpt]["ring_min"] or
                ring > constants.d_moduleDetails[self.args.moduleType][self.args.ringOpt]["ring_max"]
            ) :
                
                continue
            
            # Odd/even rings
            if (self.args.ringOpt == constants.odd_str and not ring%2) :
                
                continue
            
            elif (self.args.ringOpt == constants.even_str and ring%2) :
                
                continue
            
            if (numpy.isnan(r)) :
                
                continue
            
            ring = int(ring)
            
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
            
            xInn1 = self.origin_x0+rInn*numpy.cos(phiInn1)
            yInn1 = self.origin_y0+rInn*numpy.sin(phiInn1)
            
            xInn2 = self.origin_x0+rInn*numpy.cos(phiInn2)
            yInn2 = self.origin_y0+rInn*numpy.sin(phiInn2)
            
            xOut1 = self.origin_x0+rOut*numpy.cos(phiOut1)
            yOut1 = self.origin_y0+rOut*numpy.sin(phiOut1)
            
            xOut2 = self.origin_x0+rOut*numpy.cos(phiOut2)
            yOut2 = self.origin_y0+rOut*numpy.sin(phiOut2)
            
            xMid1 = self.origin_x0+r*numpy.cos(phiMid1)
            yMid1 = self.origin_y0+r*numpy.sin(phiMid1)
            
            xMid2 = self.origin_x0+r*numpy.cos(phiMid2)
            yMid2 = self.origin_y0+r*numpy.sin(phiMid2)
            
            #print([xInn1, xInn2, xOut2, xOut1], [yInn1, yInn2, yOut2, yOut1])
            
            
            # Attach image
            if (self.loadInfo is None) :
                
                nearestImgIdx = self.imgInfo.get_nearestImageIdx(0.5*(xMid1+xMid2), 0.5*(yMid1+yMid2))
            
            else :
                
                nearestImgIdx = self.imgInfo.get_imgIdx_from_fName(self.loadInfo[cfoamLabel])
            
            
            if (self.args.moduleType == constants.module_PS_str) :
                
                self.l_cfoamNum[ring-1] += 1
                
                
                # C-foam label
                cfoamLabel = "R%d/CF%d" %(ring, self.l_cfoamNum[ring-1])
                self.l_cfoamLabel.append([0.5*(xInn1+xInn2), 0.5*(yInn1+yInn2), cfoamLabel])
                
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
                axis_imgDee.add_patch(cfoamBox)
                
                self.d_geomObj[cfoamLabel].add_geometryArtist(cfoamBox, cfoamBoxLabel)
                
                
                # Longitudinal central profile
                profLabel = "%s_prof" %(cfoamLabel)
                
                profLine = axis_imgDee.plot([xMid1, xMid2], [yMid1, yMid2], color = color, linewidth = 1, picker = True, pickradius = 3, label = profLabel, zorder = constants.zorder_geometryMesh)[0]
                
                rr_profLine, cc_profLine = skimage.draw.line(int(numpy.round(yMid2)), int(numpy.round(xMid2)), int(numpy.round(yMid1)), int(numpy.round(xMid1)))
                
                rr_profLine = rr_profLine - self.imgInfo.l_imgExtent_pixelY[nearestImgIdx][0]
                cc_profLine = cc_profLine - self.imgInfo.l_imgExtent_pixelX[nearestImgIdx][0]
                
                #for idx in range(0, len(rr_profLine)) :
                #    
                #    if (rr_profLine[idx] < 0 or rr_profLine[idx] >= self.imgInfo.nRow or cc_profLine[idx] < 0 or cc_profLine[idx] >= self.imgInfo.nCol) :
                #        
                #        rr_profLine[idx] = 0
                #        cc_profLine[idx] = 0
                
                self.d_geomObj[cfoamLabel].add_geometryArtist(profLine, profLabel)
                
                #self.d_geomObj[cfoamLabel].add_profileLine(rr_profLine, cc_profLine, profLabel)
                self.d_geomObj[cfoamLabel].add_profileLine(
                    r1 = numpy.round(yMid2),
                    c1 = numpy.round(xMid2),
                    r2 = numpy.round(yMid1),
                    c2 = numpy.round(xMid1),
                    #offsetRow = -self.imgInfo.l_imgExtent_pixelY[nearestImgIdx][0],
                    #offsetCol = -self.imgInfo.l_imgExtent_pixelX[nearestImgIdx][0],
                    label = profLabel
                )
                
                
                # C-foam text
                axis_imgDee.text(
                    0.5*(xInn1+xInn2),
                    0.5*(yInn1+yInn2),
                    cfoamLabel,
                    rotation = 90 - (180-phi_deg),
                    size = "small",
                    horizontalalignment = "center",
                    verticalalignment = "center",
                    zorder = constants.zorder_geometryText,
                )
            
            
            elif (self.args.moduleType == constants.module_2S_str) :
                
                self.l_module2SNum[ring-1] += 1
                
                insert_outR = self.unitConv.mm_to_pix(self.d_geometry["insert_outR"][idx])
                
                # Module label
                module2SLabel = "R%d/2S%d" %(ring, self.l_module2SNum[ring-1])
                self.l_module2SLabel.append([0.5*(xInn1+xInn2), 0.5*(yInn1+yInn2), module2SLabel])
                
                self.d_geomObj[module2SLabel] = Module2SInfo.Module2SInfo(
                    imgInfo = self.imgInfo,
                    imgIdx = nearestImgIdx,
                    label = module2SLabel,
                )
                
                
                # 2S module box
                module2SBoxLabel = "%s_box" %(module2SLabel)
                
                module2SBox_xx = [xInn1, xInn2, xOut2, xOut1]
                module2SBox_yy = [yInn1, yInn2, yOut2, yOut1]
                
                #rr, cc = skimage.draw.polygon_perimeter(module2SBox_yy, module2SBox_xx, shape = arr_dee_shape)
                
                module2SBox = numpy.array([[pt[0], pt[1]] for pt in zip(module2SBox_xx, module2SBox_yy)])
                module2SBox = matplotlib.patches.Polygon(module2SBox, color = color, fill = False, picker = None, label = module2SBoxLabel, zorder = constants.zorder_geometryMesh)
                axis_imgDee.add_patch(module2SBox)
                
                self.d_geomObj[module2SLabel].add_geometryArtist(module2SBox, module2SBoxLabel)
                
                
                insertCenter_xx = [xInn1, xInn2, xMid1, xMid2, xOut2, xOut1]
                insertCenter_yy = [yInn1, yInn2, yMid1, yMid2, yOut2, yOut1]
                
                
                for iInsert, insertPos in enumerate(zip(insertCenter_xx, insertCenter_yy)) :
                    
                    insertLabel = "%s_ins%d" %(module2SLabel, iInsert+1)
                    
                    insertCirc = matplotlib.patches.Circle(insertPos, radius = insert_outR, color = color, fill = False, picker = True, label = insertLabel, zorder = constants.zorder_geometryMesh)
                    axis_imgDee.add_patch(insertCirc)
                    
                    self.d_geomObj[module2SLabel].add_geometryArtist(insertCirc, insertLabel)
                
                
                ang = 90 - (180-phi_deg) + 90
                
                ang = (ang-180) if (ang > 90) else ang
                
                axis_imgDee.text(
                    0.5*(xMid1+xMid2),
                    0.5*(yMid1+yMid2),
                    module2SLabel,
                    rotation = ang,
                    size = "small",
                    horizontalalignment = "center",
                    verticalalignment = "center",
                    zorder = constants.zorder_geometryText,
                )
        
        
        axis_imgDee.set_xticks([self.origin_x0], minor = True)
        axis_imgDee.set_yticks([self.origin_y0], minor = True)
        
        axis_imgDee.xaxis.grid(True, which = "minor")
        axis_imgDee.yaxis.grid(True, which = "minor")
        
        axis_imgDee.autoscale_view()
        
        axis_imgDee.figure.canvas.draw()
    
    
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
    
    
    def attach_cfoam_image(self, cfoamLabel, imgName) :
        
        imgIdx = self.imgInfo.get_imgIdx_from_fName(fName = imgName)
        
        self.d_geomObj[cfoamLabel].set_imgIdx(imgIdx)
        
        #print((-self.imgInfo.l_imgExtent_pixelY[imgIdx][0], -self.imgInfo.l_imgExtent_pixelX[imgIdx][0]))
        
        
    
    
    def get_saveInfo(self) :
        
        d_saveInfo = {}
        
        d_saveInfo[self.originVarName_x0] = self.origin_x0
        d_saveInfo[self.originVarName_y0] = self.origin_y0
        
        for key in self.d_geomObj :
            
            d_saveInfo[key] = self.d_geomObj[key].get_imgName()
        
        return d_saveInfo
    
    
    #def __del__(self) :
    #    
    #    print("Destroying:", type(self))
    #    
    #    self.tkroot_profile.destroy()
