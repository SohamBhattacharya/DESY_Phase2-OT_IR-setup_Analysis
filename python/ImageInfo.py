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
from tkinter import ttk

import colors
import constants
import utils


class ImageInfo :
    
    def __init__(
        self,
        #tkroot,
        args,
    ) :
        self.origin_x0 = 0
        self.origin_y0 = 0
        
        self.inputFileNamePattern = r"%s/%s" %(args.inputDir, args.inputPattern)
        self.inputFileNamePattern = self.inputFileNamePattern.replace("XXX", r"(\d+)")
        self.inputFileNamePattern = self.inputFileNamePattern.replace("YYY", r"(\d+)")
        
        print(self.inputFileNamePattern)
        
        self.l_inputFileName = glob.glob("%s/**" %(args.inputDir))
        self.l_inputFileName = [fName for fName in self.l_inputFileName if re.match(self.inputFileNamePattern, fName)]
        
        print(self.l_inputFileName)
        
        self.l_inputData = []
        
        self.l_motorX = []
        self.l_motorY = []
        
        for iFile, fName in enumerate(self.l_inputFileName) :
            
            #cfoam_m20deg_lampoff_834_677835
            
            print("Opening file: %s" %(fName))
            
            fName_pattern = r"%s%s" %(args.inputPattern, args.inputExt)
            
            (motorX, motorY) = re.findall(self.inputFileNamePattern, fName)[0]
            
            motorX = int(motorX)
            motorY = int(motorY)
            
            if (abs(motorX-2**32) < motorX) :
                
                motorX -= 2**32
            
            print(motorX, motorY)
            
            self.l_motorX.append(motorX)
            self.l_motorY.append(motorY)
            
            self.l_inputData.append(numpy.loadtxt(
                fname = fName,
                dtype = numpy.float32,
                #dtype = numpy.float,
                delimiter = "\t",
                skiprows = 9,
                usecols = list(range(0, args.nCol)),
                encoding = args.inputEncoding,
            ))
        
        
        self.nRow = self.l_inputData[0].shape[0]
        self.nCol = self.l_inputData[0].shape[1]
        
        assert (self.nCol == args.nCol), "Mismatch in given (%d) and encountered (%d) value of \"nCol\"" %(args.nCol, self.nCol)
        
        self.min_motorX = min(self.l_motorX)# - motor_stepX_to_pix(self.nCol/2, inv = True)
        self.max_motorX = max(self.l_motorX)# + motor_stepX_to_pix(self.nCol/2, inv = True)
        
        self.min_motorY = min(self.l_motorY)
        self.max_motorY = max(self.l_motorY)
        
        self.widthX_motor = self.max_motorX - self.min_motorX
        self.widthY_motor = self.max_motorY - self.min_motorY
        
        self.widthX_pix = int(utils.motor_stepX_to_pix(self.widthX_motor) + self.nCol)
        self.widthY_pix = int(utils.motor_stepY_to_pix(self.widthY_motor) + self.nRow)
        
        #print(min(l_motorX), max(l_motorX), max(l_motorX)-min(l_motorX))
        #print(min(l_motorY), max(l_motorY), max(l_motorY)-min(l_motorY))
        
        print(
            "min_motorX %f, max_motorX %f, widthX_motor %f, widthX_pix %f, "
            
        %(
            self.min_motorX, self.max_motorX, self.widthX_motor, self.widthX_pix,
        ))
        
        print(
            "min_motorY %f, max_motorY %f, widthY_motor %f, widthY_pix %f, "
            
        %(
            self.min_motorY, self.max_motorY, self.widthY_motor, self.widthY_pix,
        ))
        
        #print(l_inputData[0].shape)
        #print(l_inputData[50].shape)
        
        
        self.arr_stitchedDeeImg = numpy.full((self.widthY_pix, self.widthX_pix), fill_value = numpy.nan, dtype = numpy.float)#, dtype = numpy.float16)
        print("arr_stitchedDeeImg.shape", self.arr_stitchedDeeImg.shape)
        
        self.minTemp = +9999
        self.maxTemp = -9999
        
        self.l_imgCenter_pixelX = []
        self.l_imgCenter_pixelY = []
        
        self.l_imgExtent_pixelX = []
        self.l_imgExtent_pixelY = []
        
        for iImg, arr_img in enumerate(self.l_inputData) :
            
            motorX = self.l_motorX[iImg] - self.min_motorX
            motorY = self.l_motorY[iImg] - self.min_motorY
            
            pixelX_lwr = int(utils.motor_stepX_to_pix(motorX))# - self.nCol/2)
            pixelY_lwr = int(utils.motor_stepY_to_pix(motorY))
            
            pixelX_upr = int(pixelX_lwr + self.nCol)
            pixelY_upr = int(pixelY_lwr + self.nRow)
            
            imgCenter_pixelX = 0.5*(pixelX_lwr+pixelX_upr)
            imgCenter_pixelY = 0.5*(pixelY_lwr+pixelY_upr)
            
            self.l_imgExtent_pixelX.append((pixelX_lwr, pixelX_upr))
            self.l_imgExtent_pixelY.append((pixelY_lwr, pixelY_upr))
            
            self.l_imgCenter_pixelX.append(imgCenter_pixelX)
            self.l_imgCenter_pixelY.append(imgCenter_pixelY)
            
            
            #print(pixelX, pixelX+nCol)
            #print(pixelY, pixelY+nRow)
            #print(arr_stitchedDeeImg[pixelY: pixelY+nRow, pixelX: pixelX+nCol].shape)
            #print(arr_img.shape)
            self.arr_stitchedDeeImg[pixelY_lwr: pixelY_upr, pixelX_lwr: pixelX_upr] = arr_img
            
            
            #self.minTemp = arr_img.min() if (arr_img.min() < self.minTemp) else self.minTemp
            #self.maxTemp = arr_img.max() if (arr_img.max() > self.maxTemp) else self.maxTemp
        
        
        self.l_imgCenter_pixelX_backup = self.l_imgCenter_pixelX.copy()
        self.l_imgCenter_pixelY_backup = self.l_imgCenter_pixelY.copy()
        
        self.l_imgExtent_pixelX_backup = self.l_imgExtent_pixelX.copy()
        self.l_imgExtent_pixelY_backup = self.l_imgExtent_pixelY.copy()
        
        
        temp_mean = numpy.nanmean(self.arr_stitchedDeeImg)
        temp_std = numpy.nanstd(self.arr_stitchedDeeImg)
        
        self.minTemp = temp_mean - 3*temp_std
        self.maxTemp = temp_mean + 3*temp_std
        
        print("minTemp %f, maxTemp %f" %(self.minTemp, self.maxTemp))
        
        self.l_fig_inputImg = [None] * len(self.l_inputData)
        
        
        self.colormap = matplotlib.cm.get_cmap("nipy_spectral").copy()
        self.colormap.set_under(color = "w")
        
        
        self.time_lastPickedImage = 0
    
    
    def updateImageExtent(self, idx, imgExtent_pixelX, imgExtent_pixelY) :
        
        imgCenter_pixelX = 0.5*(imgExtent_pixelX[0]+imgExtent_pixelX[1])
        imgCenter_pixelY = 0.5*(imgExtent_pixelY[0]+imgExtent_pixelY[1])
        
        self.l_imgExtent_pixelX[idx] = tuple(imgExtent_pixelX)
        self.l_imgExtent_pixelY[idx] = tuple(imgExtent_pixelY)
        
        self.l_imgCenter_pixelX[idx] = imgCenter_pixelX
        self.l_imgCenter_pixelX[idx] = imgCenter_pixelY
    
    
    def resetImageExtent(self, idx) :
        
        dX = self.l_imgExtent_pixelX[idx][0] - self.l_imgExtent_pixelX_backup[idx][0]
        dY = self.l_imgExtent_pixelY[idx][0] - self.l_imgExtent_pixelY_backup[idx][0]
        
        self.updateImageExtent(idx, self.l_imgExtent_pixelX_backup[idx], self.l_imgExtent_pixelY_backup[idx])
        
        return (dX, dY)
    
    
    def get_nearestImageIdx(self, pixelX, pixelY, maxDist = None) :
        
        minDist2 = sys.float_info.max
        nearestIdx = -1
        
        maxDist2 = maxDist*maxDist if (maxDist is not None) else sys.float_info.max
        
        for idx, (imgX, imgY) in enumerate(zip(self.l_imgCenter_pixelX, self.l_imgCenter_pixelY)) :
            
            dist2 = (imgX-pixelX)**2 + (imgY-pixelY)**2
            
            if (dist2 < minDist2 and dist2 < maxDist2) :
                
                minDist2 = dist2
                nearestIdx = idx
        
        
        return nearestIdx
    
    
    def get_cfoamInfo(self, fName) :
        
        cfoamInfo = None
        
        for key in self.d_cfoamInfo :
            
            if (self.l_inputFileName[self.d_cfoamInfo[key].imgIdx] == fName) :
                
                cfoamInfo = self.d_cfoamInfo[key]
                break
        
        return cfoamInfo
    
    
    def draw(self) :
        
        self.tkroot_stitchedDee = tkinter.Toplevel()
        self.tkroot_stitchedDee.wm_title("Stitched image")
        self.tkroot_stitchedDee.bind_all("<Button-1>", lambda event: event.widget.focus_set())
        
        self.fig_stitchedDee = matplotlib.figure.Figure(figsize = [10, 8])
        self.fig_stitchedDee.canvas = FigureCanvasTkAgg(self.fig_stitchedDee, master = self.tkroot_stitchedDee)
        
        #self.fig_stitchedDee.canvas.mpl_connect("pick_event", self.on_pick)
        
        self.axis_stitchedDee = self.fig_stitchedDee.add_subplot(1, 1, 1)
        self.axis_stitchedDee.set_aspect("equal", "box")
        
        self.axis_stitchedDee.set_autoscale_on(True)
        
        #img = self.axis_stitchedDee.imshow(
        #    self.arr_stitchedDeeImg,
        #    #norm = matplotlib.colors.LogNorm(vmin = 1e-6, vmax = 1.0),
        #    #norm = matplotlib.colors.Normalize(vmin = minTemp, vmax = maxTemp, clip = False),
        #    origin = "upper",
        #    cmap = self.colormap,
        #    vmin = self.minTemp,
        #    vmax = self.maxTemp,
        #    alpha = 0.7,
        #)
        
        self.l_inputImg = []
        
        for imgIdx, arr_img in enumerate(self.l_inputData) :
            
            self.l_inputImg.append(self.axis_stitchedDee.imshow(
                arr_img,
                origin = "upper",
                extent = self.l_imgExtent_pixelX[imgIdx]+self.l_imgExtent_pixelY[imgIdx][::-1],
                cmap = self.colormap,
                vmin = self.minTemp,
                vmax = self.maxTemp,
                zorder = constants.zorder_deeImage,
                picker = True,
                label = self.l_inputFileName[imgIdx],
            ))
        
        self.fig_stitchedDee.colorbar(
            self.l_inputImg[0],
            ax = self.axis_stitchedDee,
            fraction = 0.046*(self.arr_stitchedDeeImg.shape[0]/self.arr_stitchedDeeImg.shape[1])
        )
        
        
        self.axis_stitchedDee.set_xlim((
            min(self.l_imgExtent_pixelX, key = lambda x: x[0])[0],
            max(self.l_imgExtent_pixelX, key = lambda x: x[1])[1],
        ))
        
        self.axis_stitchedDee.set_ylim((
            max(self.l_imgExtent_pixelY, key = lambda x: x[1])[1],
            min(self.l_imgExtent_pixelY, key = lambda x: x[0])[0],
        ))
        
        self.fig_stitchedDee.tight_layout()
        
        self.fig_stitchedDee.canvas.draw()
        
        
        # Toolbar
        self.tbar_stitchedDee = NavigationToolbar2Tk(self.fig_stitchedDee.canvas, self.tkroot_stitchedDee)
        self.tbar_stitchedDee.update()
        self.fig_stitchedDee.canvas.get_tk_widget().pack(side = tkinter.TOP, fill = tkinter.BOTH, expand = 1)
        
        self.button_show_allImages = tkinter.Button(master = self.tkroot_stitchedDee, text = "All images", takefocus = 0, command = self.show_allImages)
        self.button_show_allImages.pack(side = tkinter.LEFT)
        ttk.Separator(self.tkroot_stitchedDee, orient = tkinter.VERTICAL).pack(side = tkinter.LEFT, fill = tkinter.Y, padx = 5, pady = 5)
        
        self.button_show_allImages = tkinter.Button(master = self.tkroot_stitchedDee, text = "All C-foams", takefocus = 0, command = self.show_allCfoams)
        self.button_show_allImages.pack(side = tkinter.LEFT)
        ttk.Separator(self.tkroot_stitchedDee, orient = tkinter.VERTICAL).pack(side = tkinter.LEFT, fill = tkinter.Y, padx = 5, pady = 5)
        
        self.tbox_origin = tkinter.Entry(master = self.tkroot_stitchedDee, width = 20)
        self.tbox_origin.pack(side = tkinter.LEFT)
        
        self.button_getOrigin = tkinter.Button(master = self.tkroot_stitchedDee, text = "Get origin", takefocus = 0, command = self.get_origin)
        self.button_getOrigin.pack(side = tkinter.LEFT)
        
        self.button_setOrigin = tkinter.Button(master = self.tkroot_stitchedDee, text = "Set origin [x, y]", takefocus = 0, command = self.set_origin)
        self.button_setOrigin.pack(side = tkinter.LEFT)
        ttk.Separator(self.tkroot_stitchedDee, orient = tkinter.VERTICAL).pack(side = tkinter.LEFT, fill = tkinter.Y, padx = 5, pady = 5)
    
    
    def show_allCfoams(self) :
        
        self.tkroot_allCfoams = tkinter.Toplevel()
        self.tkroot_allCfoams.wm_title("All carbon foams")
        self.tkroot_stitchedDee.bind_all("<Button-1>", lambda event: event.widget.focus_set())
        
        self.fig_allCfoams = matplotlib.figure.Figure(figsize = [10, 8])
        self.fig_allCfoams.canvas = FigureCanvasTkAgg(self.fig_allCfoams, master = self.tkroot_allCfoams)
        
        #self.fig_allCfoams.canvas.mpl_connect("pick_event", self.on_pick_image)
        
        nPlot = len(self.d_cfoamInfo)
        nPlot_row = 10
        nPlot_col = int(nPlot/nPlot_row) + int(nPlot%nPlot_row > 0)
        
        self.l_axis_allCfoams = self.fig_allCfoams.subplots(nrows = nPlot_row, ncols = nPlot_col)
        #print(nPlot, self.l_axis_allCfoams.shape)
        
        #self.fig_allCfoams.subplots_adjust(hspace = 0.01, wspace = 0.01)
        
        cenX = self.origin_x0
        cenY = self.origin_y0
        
        l_sortedKey = utils.naturalsort(list(self.d_cfoamInfo.keys()))
        
        for count, key in enumerate(l_sortedKey) :
            
            imgIdx = self.d_cfoamInfo[key].imgIdx
            
            arr_img = self.l_inputData[imgIdx]
            
            r = int(count / nPlot_col)
            c = (count - (r*nPlot_col)) % nPlot_col
            #print((r, c))
            print((self.l_imgCenter_pixelY[imgIdx], self.l_imgCenter_pixelX[imgIdx]), (r, c))
            
            label = self.l_inputFileName[imgIdx]
            
            self.l_axis_allCfoams[r, c].imshow(
                arr_img,
                origin = "upper",
                extent = self.l_imgExtent_pixelX[imgIdx]+self.l_imgExtent_pixelY[imgIdx][::-1],
                cmap = self.colormap,
                vmin = self.minTemp,
                vmax = self.maxTemp,
                #zorder = constants.zorder_deeImage,
                picker = True,
                label = label,
            )
            
            self.d_cfoamInfo[key].drawGeomArtists(axis = self.l_axis_allCfoams[r, c], reset_artists = True)
            
            self.l_axis_allCfoams[r, c].set_title(self.d_cfoamInfo[key].label, fontsize = 7, pad = 0.1)
        
        for ax in self.l_axis_allCfoams.flat :
            
            ax.axis("off")
            #ax.set_frame_on(True)
        
        self.fig_allCfoams.tight_layout(pad = 0.1, h_pad = 0.1, w_pad = 0.0)
        
        self.fig_allCfoams.canvas.draw()
        
        
        # Toolbar
        self.tbar_allCfoams = NavigationToolbar2Tk(self.fig_allCfoams.canvas, self.tkroot_allCfoams)
        self.tbar_allCfoams.update()
        self.fig_allCfoams.canvas.get_tk_widget().pack(side = tkinter.TOP, fill = tkinter.BOTH, expand = 1)
        
        self.label_allCfoams = tkinter.Entry(master = self.tkroot_allCfoams, state = "readonly")
        self.label_allCfoams.pack(side = tkinter.LEFT, fill = tkinter.X, expand = True)
        #ttk.Separator(self.tkroot_allCfoams, orient = tkinter.VERTICAL).pack(side = tkinter.LEFT, fill = tkinter.Y, padx = 5, pady = 5)
    
    
    def show_allImages(self) :
        
        self.tkroot_allImages = tkinter.Toplevel()
        self.tkroot_allImages.wm_title("All images")
        self.tkroot_stitchedDee.bind_all("<Button-1>", lambda event: event.widget.focus_set())
        
        self.fig_allImages = matplotlib.figure.Figure(figsize = [10, 8])
        self.fig_allImages.canvas = FigureCanvasTkAgg(self.fig_allImages, master = self.tkroot_allImages)
        
        self.fig_allImages.canvas.mpl_connect("pick_event", self.on_pick_image)
        
        nPlot = len(self.l_inputData)
        nPlot_row = 10
        nPlot_col = int(nPlot/nPlot_row) + int(nPlot%nPlot_row > 0)
        
        self.l_axis_allImages = self.fig_allImages.subplots(nrows = nPlot_row, ncols = nPlot_col)
        #print(nPlot, self.l_axis_allImages.shape)
        
        self.fig_allImages.subplots_adjust(hspace = 0.01, wspace = 0.01)
        
        cenX = self.origin_x0
        cenY = self.origin_y0
        
        l_sortedIdx = list(range(nPlot))
        l_sortedIdx.sort(key = lambda x: ((self.l_imgCenter_pixelY[x]-cenY)**2 + (self.l_imgCenter_pixelX[x]-cenX)**2, self.l_imgCenter_pixelY[x]))
        
        self.l_artists_temp = []
        
        for count, imgIdx in enumerate(l_sortedIdx) :
            
            arr_img = self.l_inputData[imgIdx]
            
            r = int(count / nPlot_col)
            c = (count - (r*nPlot_col)) % nPlot_col
            #print((r, c))
            print((self.l_imgCenter_pixelY[imgIdx], self.l_imgCenter_pixelX[imgIdx]), (r, c))
            
            label = self.l_inputFileName[imgIdx]
            
            self.l_axis_allImages[r, c].imshow(
                arr_img,
                origin = "upper",
                extent = self.l_imgExtent_pixelX[imgIdx]+self.l_imgExtent_pixelY[imgIdx][::-1],
                cmap = self.colormap,
                vmin = self.minTemp,
                vmax = self.maxTemp,
                #zorder = constants.zorder_deeImage,
                picker = True,
                label = label,
            )
            
            cfoamInfo = self.get_cfoamInfo(label)
            
            if (cfoamInfo is not None) :
                
                #self.l_artists_temp.extend(cfoamInfo.drawGeomArtists(axis = self.l_axis_allImages[r, c], reset_artists = True, get_artists = True))
                cfoamInfo.drawGeomArtists(axis = self.l_axis_allImages[r, c], reset_artists = True)
            
            #self.l_axis_allImages[r, c].set_xlim((
            #    self.l_imgExtent_pixelX[imgIdx]
            #))
            #
            #self.l_axis_allImages[r, c].set_ylim((
            #    self.l_imgExtent_pixelY[imgIdx][::-1]
            #))
            #
            #self.l_axis_allImages[r, c].set_aspect("equal", "box")
        
        for ax in self.l_axis_allImages.flat :
            
            ax.axis("off")
            #ax.set_frame_on(True)
        
        self.fig_allImages.tight_layout(pad = 0.1, h_pad = 0.1, w_pad = 0.1)
        
        self.fig_allImages.canvas.draw()
        
        
        # Toolbar
        self.tbar_allImages = NavigationToolbar2Tk(self.fig_allImages.canvas, self.tkroot_allImages)
        self.tbar_allImages.update()
        self.fig_allImages.canvas.get_tk_widget().pack(side = tkinter.TOP, fill = tkinter.BOTH, expand = 1)
        
        self.label_allImages = tkinter.Entry(master = self.tkroot_allImages, state = "readonly")
        self.label_allImages.pack(side = tkinter.LEFT, fill = tkinter.X, expand = True)
        #ttk.Separator(self.tkroot_allImages, orient = tkinter.VERTICAL).pack(side = tkinter.LEFT, fill = tkinter.Y, padx = 5, pady = 5)
    
    
    def get_origin(self) :
        
        text = "%0.1f, %0.1f" %(self.origin_x0, self.origin_y0)
        self.tbox_origin.delete(0, tkinter.END)
        self.tbox_origin.insert(0, text)
    
    
    def set_origin(self, xy = None) :
        
        if (xy is None) :
            
            xy = self.tbox_origin.get().strip()
            
            if (not len(xy)) :
                
                return
            
            xy = utils.clean_string(xy)
            xy = self.tbox_origin.get().split(",")
        
        
        self.origin_x0 = float(xy[0])
        self.origin_y0 = float(xy[1])
    
    
    def set_cfoamInfo(self, d_cfoamInfo) :
        
        self.d_cfoamInfo = d_cfoamInfo
    
    
    def on_pick_image(self, event) :
        
        #dt = time.time() - self.time_lastPickedImage
        #print(time.time(), self.time_lastPickedImage,  dt)
        #
        #dt_threshold = 100.0/1000
        #
        #if (dt < dt_threshold) :
        #    
        #    return
        #
        ##time.sleep(1)
        #
        #self.time_lastPickedImage += dt
        
        artist = event.artist
        
        label = artist.get_label()
        zorder = artist.get_zorder()
        
        
        cfoamInfo = self.get_cfoamInfo(label)
        assoc_cfoam = cfoamInfo.label if (cfoamInfo is not None) else "none"
        
        
        text = "Picked image (cfoam: %s): %s" %(assoc_cfoam, label)
        print(text)
        
        #self.label_allImages["text"] = text
        
        self.label_allImages.config(state = "normal")
        #self.label_allImages.config(width = len(text))
        self.label_allImages.delete(0, tkinter.END)
        self.label_allImages.insert(0, text)
        self.label_allImages.config(state = "readonly")
        
        
        
        #if (zorder == constants.zorder_deeImage) :
        #    
        #    artist.set_zorder(constants.zorder_deeImage_focus)
        #
        #elif (zorder == constants.zorder_deeImage_focus) :
        #    
        #    artist.set_zorder(constants.zorder_deeImage)
        #
        ##self.fig_stitchedDee.canvas.draw()
        ##self.fig_stitchedDee.canvas.draw_idle()
        #
        #artist.draw(self.fig_stitchedDee.canvas.renderer)
        #self.fig_stitchedDee.canvas.update()

