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

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

import colors
import constants
import BlittedCursor
import CarbonFoamInfo
import CoolingCircuit2SInfo
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
        
        self.d_coolCirc2S = {}
        self.d_coolCirc2SInfo = {}
        
        if (args.coolCircFiles is not None) :
            
            for fName in args.coolCircFiles :
                
                with open(fName, "r") as fopen :
                    
                    self.d_coolCirc2S.update(yaml.load(fopen.read(), Loader = yaml.FullLoader))
            
            #print(self.d_coolCirc2S)
        
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
        
        if (recreate and hasattr(self, "tkroot_2Sinsert")) :
            
            self.tkroot_2Sinsert.destroy()
        
        if (recreate and hasattr(self, "tkroot_coolCirc")) :
            
            self.tkroot_coolCirc.destroy()
        
        if (recreate and hasattr(self, "d_geomObj")) :
            
            for key in self.d_geomObj :
                
                self.d_geomObj[key].destroy()
        
        gc.collect()
        
        self.imgInfo.draw(recreate = True)
        
        axis_imgDee = self.imgInfo.axis_stitchedDee
        axis_imgDee.figure.canvas.mpl_connect("pick_event", self.on_pick)
        
        self.xls_geometry = pandas.ExcelFile(self.args.geomFile)
        self.dframe_geometry = self.xls_geometry.parse(0)
        
        # Clean the headers
        self.dframe_geometry.rename(columns = lambda x: x.strip(), inplace = True)
        
        # Skip empty lines
        self.dframe_geometry.dropna(how = "all", inplace = True)
        
        #print(self.dframe_geometry)
        print(self.dframe_geometry.keys())
        
        self.d_geometry = {
            "ring"             : self.dframe_geometry["Ring"].to_numpy(),
            "r"                : self.dframe_geometry["r(mm)"].to_numpy(),
            "phi"              : self.dframe_geometry["phi(deg)"].to_numpy(),
            "arcL"             : self.dframe_geometry["meanWidth(mm) (orthoradial)"].to_numpy(),
            "radL"             : self.dframe_geometry["length(mm) (radial)"].to_numpy(),
            "insert_outR"      : self.dframe_geometry["insert outer radius (mm)"].to_numpy(),
            "side"             : self.dframe_geometry["side"].to_numpy(),
        }
        
        nModule = len(self.d_geometry["r"])
        
        print("self.origin_x0, self.origin_y0:", self.origin_x0, self.origin_y0)
        
        self.imgInfo.set_origin(x0 = self.origin_x0, y0 = self.origin_y0)
        
        
        color = (1, 0, 0, 1)
        
        self.l_cfoamNum = [0]*50
        self.l_cfoamLabel = []
        
        self.l_module2SNum = [0]*50
        self.l_module2SLabel = []
        
        self.d_geomObj = {}
        self.imgInfo.set_geomObjInfo(self.d_geomObj)
        
        
        if (self.args.moduleType == constants.module_PS_str) :
            
            # Profile figure
            self.tkroot_profile = tkinter.Toplevel(class_ = "Carbon foam temperature profiles")
            self.tkroot_profile.wm_title("Carbon foam temperature profiles")
            
            self.fig_profile = matplotlib.figure.Figure(figsize = [10, 8])
            self.fig_profile.canvas = FigureCanvasTkAgg(self.fig_profile, master = self.tkroot_profile)
            
            self.fig_profile.canvas.mpl_connect("pick_event", self.on_pick)
            
            self.axis_profile = self.fig_profile.add_subplot(1, 1, 1)
            
            self.axis_profile.set_xlabel("Pixel")
            self.axis_profile.set_ylabel("Temperature [°C]")
            
            tbar = NavigationToolbar2Tk(self.fig_profile.canvas, self.tkroot_profile)
            tbar.update()
            self.fig_profile.canvas.get_tk_widget().pack(side = tkinter.TOP, fill = tkinter.BOTH, expand = 1)
            
            button = tkinter.Button(master = self.tkroot_profile, text = "Clear", command = lambda: self.clear(axis = self.axis_profile))
            button.pack(side = tkinter.LEFT)
            
            self.marker_profile = BlittedCursor.BlittedCursor_mod1(ax = self.axis_profile)
        
        elif (self.args.moduleType == constants.module_2S_str) :
            
            # Insert figure
            self.tkroot_2Sinsert = tkinter.Toplevel(class_ = "2S insert temperature")
            self.tkroot_2Sinsert.wm_title("2S insert temperature")
            
            self.fig_2Sinsert = matplotlib.figure.Figure(figsize = [10, 8])
            self.fig_2Sinsert.canvas = FigureCanvasTkAgg(self.fig_2Sinsert, master = self.tkroot_2Sinsert)
            
            self.fig_2Sinsert.canvas.mpl_connect("pick_event", self.on_pick)
            
            self.axis_2Sinsert = self.fig_2Sinsert.add_subplot(1, 1, 1)
            
            self.axis_2Sinsert.set_xlabel("Insert")
            self.axis_2Sinsert.set_ylabel("Temperature [°C]")
            
            tbar = NavigationToolbar2Tk(self.fig_2Sinsert.canvas, self.tkroot_2Sinsert)
            tbar.update()
            self.fig_2Sinsert.canvas.get_tk_widget().pack(side = tkinter.TOP, fill = tkinter.BOTH, expand = 1)
            
            button = tkinter.Button(master = self.tkroot_2Sinsert, text = "Clear", command = lambda: self.clear(axis = self.axis_2Sinsert))
            button.pack(side = tkinter.LEFT)
            
            #self.marker_2Sinsert = BlittedCursor.BlittedCursor_mod1(ax = self.axis_2Sinsert)
            
            #self.mplcursor = mplcursors.Cursor(artists = [], hover = mplcursors.HoverMode.Transient)
            
            
            # Cooling circuit figure
            self.tkroot_coolCirc = tkinter.Toplevel(class_ = "Cooling circuit: 2S inserts")
            self.tkroot_coolCirc.wm_title("Cooling circuit: 2S inserts")
            
            self.fig_coolCirc = matplotlib.figure.Figure(figsize = [10, 8])
            self.fig_coolCirc.canvas = FigureCanvasTkAgg(self.fig_coolCirc, master = self.tkroot_coolCirc)
            
            self.axis_coolCirc = self.fig_coolCirc.add_subplot(1, 1, 1)
            
            self.axis_coolCirc.set_xlabel("Insert")
            self.axis_coolCirc.set_ylabel("Temperature [°C]")
            
            tbar = NavigationToolbar2Tk(self.fig_coolCirc.canvas, self.tkroot_coolCirc)
            tbar.update()
            self.fig_coolCirc.canvas.get_tk_widget().pack(side = tkinter.TOP, fill = tkinter.BOTH, expand = 1)
            
            
            for circuitLabel in self.d_coolCirc2S :
                
                self.d_coolCirc2SInfo[circuitLabel] = CoolingCircuit2SInfo.CoolingCircuit2SInfo(
                    label = circuitLabel,
                    l_insertLabel = self.d_coolCirc2S[circuitLabel],
                    d_geomObj = self.d_geomObj,
                    axis = self.axis_coolCirc,
                )
        
        
        l_pickableArtist = []
        
        
        for idx in range(0, nModule) :
            
            ring = self.d_geometry["ring"][idx]
            r = self.unitConv.mm_to_pix(self.d_geometry["r"][idx])
            phi_deg = self.d_geometry["phi"][idx]
            phi = numpy.pi-numpy.radians(phi_deg)
            arcL = self.unitConv.mm_to_pix(self.d_geometry["arcL"][idx])
            radL = self.unitConv.mm_to_pix(self.d_geometry["radL"][idx])
            
            side = self.d_geometry["side"][idx]
            
            
            if (
                (self.args.moduleType == constants.module_2S_str and side == constants.side_bottom_str) or
                (self.args.moduleType == constants.module_PS_str and self.args.side == constants.side_bottom_str)
            ) :
                
                phi_deg = 180 - phi_deg
                phi = numpy.pi - phi
            
            
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
            
            
            if (self.args.moduleType == constants.module_PS_str) :
                
                self.l_cfoamNum[ring-1] += 1
                
                color = constants.d_side_color[side]
                
                
                # C-foam label
                cfoamLabel = "R%d/CF%d" %(ring, self.l_cfoamNum[ring-1])
                self.l_cfoamLabel.append([0.5*(xInn1+xInn2), 0.5*(yInn1+yInn2), cfoamLabel])
                
                
                # Attach image
                if (self.loadInfo is None) :
                    
                    nearestImgIdx = self.imgInfo.get_nearestImageIdx(0.5*(xMid1+xMid2), 0.5*(yMid1+yMid2))
                
                else :
                    
                    nearestImgIdx = self.imgInfo.get_imgIdx_from_fName(self.loadInfo[cfoamLabel])
                
                
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
                
                profLine = axis_imgDee.plot(
                    [xMid1, xMid2],
                    [yMid1, yMid2],
                    color = color,
                    linewidth = 1,
                    picker = True,
                    pickradius = 3,
                    label = profLabel,
                    zorder = constants.zorder_geometryMesh,
                )[0]
                
                l_pickableArtist.append(profLine)
                
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
                    label = profLabel,
                )
                
                
                # C-foam text
                cfoamText = matplotlib.text.Annotation(
                    text = cfoamLabel,
                    xy = (0.5*(xInn1+xInn2), 0.5*(yInn1+yInn2)),
                    rotation = phi_deg - 90,
                    size = "small",
                    horizontalalignment = "center",
                    verticalalignment = "center",
                    zorder = constants.zorder_geometryText,
                )
                
                axis_imgDee.add_artist(cfoamText)
                self.d_geomObj[cfoamLabel].add_geometryArtist(cfoamText, "%s_label" %(cfoamLabel))
            
            
            elif (self.args.moduleType == constants.module_2S_str) :
                
                self.l_module2SNum[ring-1] += 1
                #print(side)
                
                if (side != self.args.side) :
                    
                    continue
                
                color = constants.d_side_color[side]
                
                insert_outR = self.unitConv.mm_to_pix(self.d_geometry["insert_outR"][idx])
                
                # Module label
                module2SLabel = "R%d/2S%d" %(ring, self.l_module2SNum[ring-1])
                self.l_module2SLabel.append([0.5*(xInn1+xInn2), 0.5*(yInn1+yInn2), module2SLabel])
                
                
                # Attach image
                if (self.loadInfo is None) :
                    
                    nearestImgIdx = self.imgInfo.get_nearestImageIdx(0.5*(xMid1+xMid2), 0.5*(yMid1+yMid2))
                
                else :
                    
                    nearestImgIdx = self.imgInfo.get_imgIdx_from_fName(self.loadInfo[module2SLabel])
                
                
                self.d_geomObj[module2SLabel] = Module2SInfo.Module2SInfo(
                    imgInfo = self.imgInfo,
                    imgIdx = nearestImgIdx,
                    label = module2SLabel,
                    axis_2Sinsert = self.axis_2Sinsert,
                    d_coolCirc = self.d_coolCirc2SInfo,
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
                
                
                #insertCenter_xx = [xInn1, xInn2, xMid1, xMid2, xOut1, xOut2]
                #insertCenter_yy = [yInn1, yInn2, yMid1, yMid2, yOut1, yOut2]
                
                insertCenter_xx = [xInn2, xInn1, xMid2, xOut2, xOut1]
                insertCenter_yy = [yInn2, yInn1, yMid2, yOut2, yOut1]
                
                # Simply change the order
                if (side == constants.side_bottom_str) :
                    
                    insertCenter_xx = [xInn1, xInn2, xMid2, xOut1, xOut2]
                    insertCenter_yy = [yInn1, yInn2, yMid2, yOut1, yOut2]
                
                
                for iInsert, insertPos in enumerate(zip(insertCenter_xx, insertCenter_yy)) :
                    
                    insertLabel = "%s_ins%d" %(module2SLabel, iInsert+1)
                    insertLabel_local = "%d" %(iInsert+1)
                    
                    insertDisk = matplotlib.patches.Circle(insertPos, radius = insert_outR, color = color, fill = False, picker = True, label = insertLabel, zorder = constants.zorder_geometryMesh)
                    axis_imgDee.add_patch(insertDisk)
                    l_pickableArtist.append(insertDisk)
                    
                    self.d_geomObj[module2SLabel].add_geometryArtist(insertDisk, insertLabel)
                    axis_imgDee.text(
                        x = insertPos[0],
                        y = insertPos[1]-insert_outR,
                        s = insertLabel_local,
                        size = "small",
                        horizontalalignment = "center",
                        verticalalignment = "bottom",
                        zorder = constants.zorder_geometryText,
                    )
                    
                    insertText = matplotlib.text.Annotation(
                        text = insertLabel_local,
                        xy = (insertPos[0], insertPos[1]-insert_outR),
                        size = "small",
                        horizontalalignment = "center",
                        verticalalignment = "bottom",
                        zorder = constants.zorder_geometryText,
                        #annotation_clip = False,
                    )
                    
                    self.d_geomObj[module2SLabel].add_geometryArtist(insertText, "%s_label" %(insertLabel))
                    
                    
                    self.d_geomObj[module2SLabel].add_insertDisk(
                        r = insertPos[1],
                        c = insertPos[0],
                        radius = insert_outR,
                        label = insertLabel,
                    )
                    
                    #self.mplcursor.add_highlight(insertDisk)
                    
                    #rr_insertDisk, cc_insertDisk = skimage.draw.disk(
                    #    #center = insertPos[::-1],
                    #    center = (insertPos[1]-self.imgInfo.l_imgExtent_pixelY[nearestImgIdx][0], insertPos[0]-self.imgInfo.l_imgExtent_pixelX[nearestImgIdx][0]),
                    #    radius = insert_outR,
                    #    shape = (self.imgInfo.nRow, self.imgInfo.nCol),
                    #)
                    
                    #rr_insertDisk = rr_insertDisk - self.imgInfo.l_imgExtent_pixelY[nearestImgIdx][0]
                    #cc_insertDisk = cc_insertDisk - self.imgInfo.l_imgExtent_pixelX[nearestImgIdx][0]
                    
                    #for idx in range(0, len(rr_profLine)) :
                    #    
                    #    if (rr_profLine[idx] < 0 or rr_profLine[idx] >= self.imgInfo.nRow or cc_profLine[idx] < 0 or cc_profLine[idx] >= self.imgInfo.nCol) :
                    #        
                    #        rr_profLine[idx] = 0
                    #        cc_profLine[idx] = 0
                    
                    #print("rr_insertDisk:", rr_insertDisk)
                    #print("cc_insertDisk:", cc_insertDisk)
                    
                    #self.imgInfo.l_inputData[nearestImgIdx][rr_insertDisk, cc_insertDisk] = 0
                
                
                ang = 90 - (180-phi_deg) + 90
                ang = (ang-180) if (ang > 90) else ang
                
                module2SText = matplotlib.text.Annotation(
                    text = module2SLabel,
                    xy = (0.5*(xMid1+xMid2), 0.5*(yMid1+yMid2)),
                    rotation = ang,
                    size = "small",
                    horizontalalignment = "center",
                    verticalalignment = "center",
                    zorder = constants.zorder_geometryText,
                    #annotation_clip = False,
                )
                
                axis_imgDee.add_artist(module2SText)
                self.d_geomObj[module2SLabel].add_geometryArtist(module2SText, module2SLabel)
                
                
                
        
        #axis_imgDee.set_xticks([self.origin_x0], minor = True)
        #axis_imgDee.set_yticks([self.origin_y0], minor = True)
        #
        #axis_imgDee.xaxis.grid(True, which = "minor")
        #axis_imgDee.yaxis.grid(True, which = "minor")
        
        axis_imgDee.axhline(y = self.origin_y0, color = "k", linewidth = 0.8, linestyle = "--")
        axis_imgDee.axvline(x = self.origin_x0, color = "k", linewidth = 0.8, linestyle = "--")
        
        axis_imgDee.autoscale_view()
        
        axis_imgDee.figure.canvas.draw()
        
        #self.mplcursor = mplcursors.cursor(l_pickableArtist, hover = mplcursors.HoverMode.Transient)
        #
        #self.mplcursor.connect(
        #    "add", lambda sel: sel.annotation.set_text(sel.artist.get_label())
        #)
        
        if (self.args.moduleType == constants.module_2S_str) :
            
            self.draw_coolingCircuits2S()
            
            #for circuitLabel in self.d_coolCirc2S :
            #    
            #    self.d_coolCirc2SInfo[circuitLabel].draw()
        
        
        #self.draw_coolingCircuits()
    
    
    def draw_coolingCircuits2S(self) :
        
        l_line = []
        d_insertTempAnnotation = {}
        
        for circuitLabel in self.d_coolCirc2S :
            
            self.d_coolCirc2SInfo[circuitLabel].draw()
            
            l_line.append(self.d_coolCirc2SInfo[circuitLabel].line)
            
            d_insertTempAnnotation[circuitLabel] = self.d_coolCirc2SInfo[circuitLabel].l_annotation
        
        legend = self.axis_coolCirc.legend()
        d_legline = {}
        d_legtext = {}
        d_legCoolCirc = {}
        
        for legtext, legline, origline in zip(legend.texts, legend.get_lines(), l_line) :
            
            legline.set_picker(True)
            legline.set_pickradius(3)
            d_legline[legline] = origline
            d_legtext[legline] = legtext
        
        for legline, coolCirc2SInfo in zip(legend.get_lines(), list(self.d_coolCirc2SInfo.values())) :
            
            d_legCoolCirc[legline] = coolCirc2SInfo
        
        
        def on_pick_legend(event) :
            
            legline = event.artist
            
            if (legline not in d_legline) :
                
                return
                
            visible = not d_legCoolCirc[legline].line.get_visible()
            
            alpha = 1.0 if visible else 0.3
            
            legline.set_alpha(alpha)
            legline._legmarker.set_alpha(alpha)
            d_legtext[legline].set_alpha(alpha)
            
            d_legCoolCirc[legline].set_visible(visible = visible)
            
            self.fig_coolCirc.canvas.draw()
        
        
        def on_pick_line(event, pickradius = 5) :
            
            pickradius2 = pickradius*pickradius
            
            artist = event.artist
            label = artist.get_label()
            
            if (artist not in l_line or not artist.get_visible()) :
                
                return
            
            mouseevent = event.mouseevent
            
            clickX = mouseevent.xdata
            clickY = mouseevent.ydata
            clickX, clickY = self.axis_coolCirc.transData.transform_point([clickX, clickY])
            
            xdata = artist.get_xdata()
            ydata = artist.get_ydata()
            
            a_dist2 = []
            
            for px, py in zip(xdata, ydata) :
                
                px, py = self.axis_coolCirc.transData.transform_point([px, py])
                dist2 = (px - clickX)**2 + (py - clickY)**2
                a_dist2.append(dist2)
            
            idx_minDist = numpy.argmin(a_dist2)
            minDist2 = a_dist2[idx_minDist]
            
            if (minDist2 > pickradius2) :
                
                return
            
            d_insertTempAnnotation[label][idx_minDist].set_visible(not d_insertTempAnnotation[label][idx_minDist].get_visible())
            
            self.fig_coolCirc.canvas.draw()
        
        self.fig_coolCirc.canvas.mpl_connect("pick_event", on_pick_legend)
        self.fig_coolCirc.canvas.mpl_connect("pick_event", on_pick_line)
        
        self.axis_coolCirc.autoscale_view()
        self.fig_coolCirc.tight_layout()
        self.fig_coolCirc.canvas.draw()
    
    
    def on_pick(self, event) :
        
        artist = event.artist
        
        label = artist.get_label()
        print("Picked:", artist, label)
        
        label = label.split("_")[0]
        
        if (label in self.d_geomObj) :
            
            self.d_geomObj[label].on_pick(event)
    
    
    def clear(self, axis) :
        
        for label in self.d_geomObj :
            
            if (hasattr(self.d_geomObj[label], "unplot_profiles")) :
                
                self.d_geomObj[label].unplot_profiles(axis = axis, draw = False)
            
            elif (hasattr(self.d_geomObj[label], "unplot_2Sinserts")) :
                
                self.d_geomObj[label].unplot_2Sinserts(axis = axis, draw = False)
        
        axis.figure.canvas.draw()
    
    
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
