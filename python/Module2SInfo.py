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
import mpl_toolkits.axes_grid1
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
import InsertDisk
import utils


class Module2SInfo :
    
    def __init__(
        self,
        imgInfo,
        imgIdx,
        label,
        axis_2Sinsert,
        d_coolCirc,
    ) :
        
        self.imgInfo = imgInfo
        self.imgIdx = imgIdx
        self.label = label
        
        self.offsetRow = -self.imgInfo.l_imgExtent_pixelY[imgIdx][0]
        self.offsetCol = -self.imgInfo.l_imgExtent_pixelX[imgIdx][0]
        
        self.d_geomArtist = {}
        self.d_insertDisk = {}
        
        self.d_drawnArtist = {}
        
        self.axis_2Sinsert = axis_2Sinsert
        self.d_coolCirc = d_coolCirc
        
        self.tkroot_img = None
        self.fig_img = None
        self.marker_img = None
        self.cid_marker = None
        
        self.event_startDrag = None
        self.l_cid_dragImg = []
    
    
    def destroy(self) :
        
        if (self.tkroot_img is not None and tkinter.Toplevel.winfo_exists(self.tkroot_img)) :
            
            self.tkroot_img.destroy()
    
    
    def get_imgName(self) :
        
        return self.imgInfo.l_inputFileName[self.imgIdx]
    
    
    def attach_image(self, imgName) :
        
        imgName = utils.clean_string(imgName)
        
        imgIdx = self.imgInfo.get_imgIdx_from_fName(fName = imgName)
        
        self.set_imgIdx(imgIdx)
        
        #if (self.fig_img is not None) :
        #    
        #    self.on_fig_close(event = None)
        #    self.draw()
        
        self.destroy()
        self.draw()
    
    
    def set_imgIdx(self, imgIdx) :
        
        #self.reset()
        
        self.imgIdx = imgIdx
        
        self.offsetRow = -self.imgInfo.l_imgExtent_pixelY[imgIdx][0]
        self.offsetCol = -self.imgInfo.l_imgExtent_pixelX[imgIdx][0]
        
        #self.reset()
        
        self.update_features(dRow = 0, dCol = 0)
        
        self.centerImage()
        
        #self.update_features(
        #    dRow = 0,
        #    dCol = 0,
        #)
        
    
    
    def resetAllArtists(self) :
        
        for key in self.d_geomArtist :
            
            utils.reset_artist(self.d_geomArtist[key])
    
    
    def add_geometryArtist(self, artist, label) :
        
        #print("Adding artist:", artist)
        
        self.d_geomArtist[label] = copy.copy(artist)
        utils.reset_artist(self.d_geomArtist[label])
    
    
    def add_insertDisk(
        self,
        r, c,
        radius,
        label,
    ) :
        
        self.d_insertDisk[label] = InsertDisk.InsertDisk(
            r = r,
            c = c,
            radius = radius,
            shape = (self.imgInfo.nRow, self.imgInfo.nCol),
            offsetRow = self.offsetRow,
            offsetCol = self.offsetCol,
        )
    
    
    def on_fig_close(self, event) :
        
        #if (self.fig_img == event.canvas.figure) :
        #if (self.fig_img is not None) :
        
        try :
            
            self.fig_img.clf()
            matplotlib.pyplot.close(self.fig_img)
            
            for axis in self.fig_img.get_axes() :
                
                axis.clf()
                axis.remove()
            
            self.resetAllArtists()
            
            self.fig_img = None
            
            self.tkroot_img.destroy()
            self.tkroot_img = None
            
            gc.collect()
            
            print("Closed image %s" %(self.label))
        
        except :
            
            pass
    
    
    def get_minTemp(self, label) :
        
        rr = self.d_insertDisk[label].rr
        cc = self.d_insertDisk[label].cc
        
        if (not len(rr) or not len(cc)) :
            
            return None
        
        #print(rr, cc)
        
        nPix = len(rr)
        
        ##minTemp = min(self.imgInfo.l_inputData[self.imgIdx][rr, cc])
        minTemp = self.imgInfo.l_inputData[self.imgIdx][rr, cc].min()
        
        #arr = self.imgInfo.l_inputData[self.imgIdx][rr, cc]
        ##print(arr.shape)
        #sorted_idx = list(zip(*numpy.unravel_index(numpy.argsort(arr, axis = None), arr.shape)))
        #minTemp = (arr[sorted_idx[0]] + arr[sorted_idx[1]] + arr[sorted_idx[2]] + arr[sorted_idx[3]] + arr[sorted_idx[4]]) / 5
        
        return minTemp
    
    
    #def get_minTemp_all(self) :
    #    
    #    xx = []
    #    yy = []
    #    
    #    for key in utils.naturalsort(list(self.d_insertDisk.keys())) :
    #        
    #        minTemp = self.get_minTemp(label = key)
    #        
    #        yy.append(minTemp)
    #    
    #    xx = list(range(1, len(yy)+1))
    #    
    #    return (xx, yy)
    
    
    def plot_minTemp(self, label, axis, color = "black", update = False) :
        
        #print(label, self.get_minTemp(label = label))
        
        if (label in self.d_drawnArtist and not update) :
            
            return
        
        xx = len(axis.get_lines())+1 if (label not in self.d_drawnArtist) else self.d_drawnArtist[label].get_xdata()#[0]
        yy = self.get_minTemp(label = label)
        
        if (update) :
            
            self.d_drawnArtist[label].set_xdata(xx)
            self.d_drawnArtist[label].set_ydata(yy)
        
        else :
            
            self.d_drawnArtist[label] = axis.plot(xx, yy, color = color, marker = "o", markersize = 5,  linewidth = 0, label = label, picker = True, pickradius = 3)[0]
            axis.legend()
        
        axis.relim()
        axis.autoscale_view()
        
        axis.figure.canvas.draw()
    
    
    def unplot_2Sinsert(self, label, axis) :
        
        if (label not in self.d_drawnArtist) :
            
            return
        
        self.d_drawnArtist[label].remove()
        del self.d_drawnArtist[label]
        #self.d_2SinsertArtist[label] = None
        
        axis.legend()
        axis.figure.canvas.draw()
    
    
    def unplot_2Sinserts(self, axis, draw = True) :
        
        if (not len (self.d_drawnArtist)) :
            
            return
        
        for key in self.d_drawnArtist :
            
            self.d_drawnArtist[key].remove()
        
        self.d_drawnArtist.clear()
        
        axis.legend()
        
        if (draw) :
            
            axis.figure.canvas.draw()
    
    
    def get_title(self) :
        
        title = []
        
        title.append(
            "$\\bf{File\\ path:}$ %s" %(self.imgInfo.l_inputFilePath[self.imgIdx]),
        )
        
        title.append(
            "$\\bf{File\\ name:}$ %s" %(self.imgInfo.l_inputFilePath[self.imgIdx].split("/")[-1]),
        )
        
        title.append(
            "$\\bf{Original\\ extent:}$ x [%d, %d], y [%d, %d]" %(*self.imgInfo.l_imgExtent_pixelX_backup[self.imgIdx], *self.imgInfo.l_imgExtent_pixelY_backup[self.imgIdx]),
        )
        
        title.append(
            "$\\bf{Current\\ extent:}$ x [%d, %d], y [%d, %d]" %(*self.imgInfo.l_imgExtent_pixelX[self.imgIdx], *self.imgInfo.l_imgExtent_pixelY[self.imgIdx]),
        )
        
        return "\n".join(title)
    
    
    def drawGeomArtists(self, axis = None, reset_artists = False, get_artists = False) :
        
        ax = axis if (axis is not None) else self.axis_img
        
        l_artist = []
        
        for key in self.d_geomArtist :
            
            artist = self.d_geomArtist[key]
            
            if (reset_artists) :
                
                artist = copy.copy(artist)
                utils.reset_artist(artist)
            
            artist.set_transform(ax.transData)
            
            ax.add_artist(artist)
            #self.axis_img.draw_artist(self.d_geomArtist[key])
            
            if (get_artists) :
                
                l_artist.append(artist)
        
        if (get_artists) :
            
            return l_artist
    
    
    def draw(self) :
        
        if (self.fig_img is None) :
            
            figName = "%s" %(self.label)
            
            self.tkroot_img = tkinter.Toplevel(class_ = figName)
            self.tkroot_img.wm_title(figName)
            
            self.fig_img = matplotlib.figure.Figure(figsize = [8, 5])
            self.fig_img.canvas = FigureCanvasTkAgg(self.fig_img, master = self.tkroot_img)
            self.fig_img.canvas.get_tk_widget().pack(side = tkinter.TOP, fill = tkinter.BOTH, expand = True)
            
            #self.fig_img = matplotlib.pyplot.figure(figName, figsize = [5, 5])
            
            title = "\n".join([
                self.imgInfo.l_inputFileName[self.imgIdx],
                "Extent x: [%d, %d], y: [%d, %d]" %(*self.imgInfo.l_imgExtent_pixelX[self.imgIdx], *self.imgInfo.l_imgExtent_pixelY[self.imgIdx]),
            ])
            
            #self.fig_img.suptitle("\n".join(textwrap.wrap(self.imgInfo.l_inputFileName[self.imgIdx], 80)), fontsize = 9)
            self.fig_img.suptitle(self.get_title(), x = 0, fontsize = 9, horizontalalignment = "left", wrap = True)#, usetex = True)
            
            self.fig_img.canvas.mpl_connect("close_event", self.on_fig_close)
            self.fig_img.canvas.mpl_connect("pick_event", self.on_pick)
            self.fig_img.canvas.mpl_connect("button_press_event", self.on_button_press)
            #self.cid_marker = self.fig_img.canvas.mpl_connect("motion_notify_event", self.animate_marker)
            
            self.axis_img = self.fig_img.add_subplot(1, 1, 1)
            self.axis_img.set_aspect("equal", "box")
            self.axis_img.set_xlim(self.imgInfo.l_imgExtent_pixelX[self.imgIdx])
            self.axis_img.set_ylim(self.imgInfo.l_imgExtent_pixelY[self.imgIdx][::-1])
            
            self.axis_img.set_xlabel("Pixel x", fontsize = "x-large", fontweight = "bold")
            self.axis_img.set_ylabel("Pixel y", fontsize = "x-large", fontweight = "bold")
            self.axis_img.tick_params(axis = "both", labelsize = "x-large")
            
            #self.axis_img.autoscale(enable = True)
            
            #self.axis_img.set_title(title, loc = "left", fontsize = 7, wrap = True)
            
            arr_inputImg = self.imgInfo.l_inputData[self.imgIdx]
            
            self.img = self.axis_img.imshow(
                arr_inputImg,
                origin = "upper",
                extent = self.imgInfo.l_imgExtent_pixelX[self.imgIdx]+self.imgInfo.l_imgExtent_pixelY[self.imgIdx][::-1],
                #extent = (0, self.imgInfo.widthX_pix, self.imgInfo.widthY_pix, 0),
                cmap = self.imgInfo.colormap,
                vmin = self.imgInfo.minTemp,
                vmax = self.imgInfo.maxTemp,
            )
            
            divider = mpl_toolkits.axes_grid1.make_axes_locatable(self.axis_img)
            cax = divider.append_axes("right", size = "3%", pad = 0.1)
            
            cax.tick_params(axis = "both", labelsize = "x-large")
            
            cbar = self.fig_img.colorbar(
                self.img,
                cax = cax,
                #ax = self.axis_img,
                #fraction = 0.046*(arr_inputImg.shape[0]/arr_inputImg.shape[1]),
                label = "Temperature [°C]",
            )
            
            cbar.set_label("Temperature [°C]", size = "x-large", weight = "bold")
            
            self.background = self.fig_img.canvas.copy_from_bbox(self.axis_img.get_figure().bbox)
            
            
            self.drawGeomArtists()
            
            self.fig_img.tight_layout()
            
            self.marker_img = BlittedCursor.BlittedCursor_mod1(ax = self.axis_img, picker = True)
            
            #matplotlib.pyplot.show(block = False)
            
            
            frame = tkinter.Frame(master = self.tkroot_img)
            frame.pack(side = tkinter.TOP, fill = tkinter.X)
            
            button = tkinter.Button(master = frame, text = "Reset", takefocus = 0, command = self.reset)
            button.pack(side = tkinter.LEFT)
            
            button = tkinter.Button(master = frame, text = "Center image", takefocus = 0, command = self.centerImage)
            button.pack(side = tkinter.LEFT)
            
            frame = tkinter.Frame(master = self.tkroot_img)
            frame.pack(side = tkinter.TOP, fill = tkinter.X)
            
            self.svar_imgName = tkinter.StringVar()
            entry = tkinter.Entry(master = frame, textvariable = self.svar_imgName)
            entry.pack(side = tkinter.LEFT, fill = tkinter.X, expand = True)
            
            button = tkinter.Button(master = frame, text = "Set image", takefocus = 0, command = lambda: self.attach_image(self.svar_imgName.get()))
            button.pack(side = tkinter.LEFT, fill = tkinter.X)
            
            
            # Toolbar
            toolbar = NavigationToolbar2Tk(self.fig_img.canvas, self.tkroot_img, pack_toolbar = False)
            toolbar.update()
            toolbar.pack(side = tkinter.BOTTOM, fill = tkinter.X)
        
        else :
            
            #self.fig_img.canvas.manager.window.raise_()
            self.tkroot_img.lift()
    
    
    def choose_color(self, l_skipColor) :
        
        color = None
        
        for color in colors.highContrastColors_1 :
            
            if (color not in l_skipColor) :
                
                break
        
        return color
    
    
    def get_usedColors(self, axis, l_objectType) :
        
        l_usedColor = []
        
        for ele in axis.get_children() :
            
            type_str = str(type(ele))
            
            for t in l_objectType :
                
                if (t in type_str and hasattr(ele, "get_color")) :
                    
                    l_usedColor.append(ele.get_color())
        
        return l_usedColor
    
    
    def on_pick(self, event, plot_features = True) :
        
        artist = event.artist
        
        label = artist.get_label()
        #print("Picked:", artist, label)
        
        label = label.split("_")[0]
        
        #self.imgInfo.on_mouse_click(event.mouseevent)
        
        event_key = str(event.mouseevent.key).lower()
        event_button = event.mouseevent.button
        
        clickX = event.mouseevent.xdata
        clickY = event.mouseevent.ydata
        
        #print(event_key, event_button, clickX, clickY)
        
        #if (clickX is None or clickY is None) :
        #    
        #    return
        
        if (event_key == "ctrl+shift" and event_button == matplotlib.backend_bases.MouseButton.LEFT) :
            
            self.draw()
        
        elif (event_key == "shift" and event_button == matplotlib.backend_bases.MouseButton.LEFT) :
            
            #self.draw()
            
            #color = "black"
            color = self.choose_color(l_skipColor = self.get_usedColors(axis = self.axis_2Sinsert, l_objectType = "Line2D"))
            
            self.plot_minTemp(
                label = artist.get_label(),
                axis = self.axis_2Sinsert,
                color = color,
            )
        
        elif (event_key == "shift" and event_button == matplotlib.backend_bases.MouseButton.RIGHT) :
            
            self.unplot_2Sinsert(
                label = artist.get_label(),
                axis = self.axis_2Sinsert,
            )
    
    
    def update_features(
        self,
        dRow,
        dCol,
    ) :
        
        for key in self.d_insertDisk :
            
            rr, cc = self.d_insertDisk[key].setAndGetDisk(
                dRow = dRow,
                dCol = dCol,
                offsetRow = self.offsetRow,
                offsetCol = self.offsetCol,
            )
            
            if key in self.d_drawnArtist :
                
                self.plot_minTemp(
                    label = key,
                    axis = self.axis_2Sinsert,
                    update = True,
                )
        
        for coolCircLabel in self.d_coolCirc :
            
            self.d_coolCirc[coolCircLabel].update(l_insertLabel = list(self.d_insertDisk.keys()))
    
    
    def update_imgExtent(self, new_extent, dX, dY) :
        
        self.imgInfo.updateImageExtent(idx = self.imgIdx, imgExtent_pixelX = new_extent[0: 2], imgExtent_pixelY = new_extent[2: 4][::-1])
        
        if (hasattr(self, "img")) :
            
            self.img.set_extent(new_extent)
            
            self.axis_img.set_xlim(*new_extent[0: 2])
            self.axis_img.set_ylim(*new_extent[2: 4])
            
            self.fig_img._suptitle.set_text(self.get_title())
            
            self.fig_img.canvas.draw()
        
        self.update_features(dY, dX)
    
    
    def reset(self) :
        
        dX, dY = self.imgInfo.resetImageExtent(idx = self.imgIdx)
        self.update_imgExtent(self.imgInfo.l_imgExtent_pixelX[self.imgIdx] + self.imgInfo.l_imgExtent_pixelY[self.imgIdx][::-1], dX, dY)
    
    
    def centerImage(self) :
        
        cenX = 0
        cenY = 0
        
        # Use the average center position
        for key in self.d_insertDisk :
            
            disk = self.d_insertDisk[key]
            
            cenX += disk.c
            cenY += disk.r
        
        cenX /= len(self.d_insertDisk)
        cenY /= len(self.d_insertDisk)
        
        dX = self.imgInfo.l_imgCenter_pixelX[self.imgIdx] - cenX
        dY = self.imgInfo.l_imgCenter_pixelY[self.imgIdx] - cenY
        
        #extent = self.img.get_extent()
        extent = self.imgInfo.l_imgExtent_pixelX[self.imgIdx] + self.imgInfo.l_imgExtent_pixelY[self.imgIdx][::-1]
        
        new_extent = (
            extent[0] - dX,
            extent[1] - dX,
            extent[2] - dY,
            extent[3] - dY,
        )
        
        print(extent, new_extent, (dX, dY), (cenX, cenY), (self.imgInfo.l_imgCenter_pixelX[self.imgIdx], self.imgInfo.l_imgCenter_pixelY[self.imgIdx]))
        
        self.update_imgExtent(new_extent, dX, dY)
    
    
    def start_drag(self, event) :
        
        if (self.event_startDrag is None) :
            
            return
        
        startX = self.event_startDrag.x
        startY = self.event_startDrag.y
        
        mouseX = event.x
        mouseY = event.y
        
        if (mouseX is None or mouseY is None) :
            
            return
        
        startX, startY = self.axis_img.transData.inverted().transform_point((startX, startY))
        mouseX, mouseY = self.axis_img.transData.inverted().transform_point((mouseX, mouseY))
        
        #print((startX, startY), "-->", (mouseX, mouseY))
        
        dX = mouseX - startX
        dY = mouseY - startY
        
        extent = self.img.get_extent()
        
        new_extent = (
            extent[0] - dX,
            extent[1] - dX,
            extent[2] - dY,
            extent[3] - dY,
        )
        
        self.update_imgExtent(new_extent, dX, dY)
        
        # Update the event
        self.event_startDrag = event
    
    
    def stop_drag(self, event) :
        
        self.fig_img.canvas.flush_events()
        
        if (len(self.l_cid_dragImg)) :
            
            self.fig_img.canvas.flush_events()
            
            #self.update_features(self.dY_sum, self.dX_sum)
            
            for cid in self.l_cid_dragImg :
                
                self.fig_img.canvas.mpl_disconnect(cid)
            
            self.l_cid_dragImg = []
    
    
    def on_button_press(self, event) :
        
        print(event)
        
        event_key = str(event.key).lower()
        event_button = event.button
        
        clickX = event.xdata
        clickY = event.ydata
        
        print(event_key, event_button, clickX, clickY)
        
        if (clickX is None or clickY is None) :
            
            return
        
        if (event_key == "ctrl+shift" and event_button == matplotlib.backend_bases.MouseButton.LEFT) :
            
            self.event_startDrag = event
            
            self.l_cid_dragImg.append(self.fig_img.canvas.mpl_connect("motion_notify_event", self.start_drag))
            
            self.l_cid_dragImg.append(self.fig_img.canvas.mpl_connect("button_release_event", self.stop_drag))
            self.l_cid_dragImg.append(self.fig_img.canvas.mpl_connect("key_release_event", self.stop_drag))
            self.l_cid_dragImg.append(self.fig_img.canvas.mpl_connect("figure_leave_event", self.stop_drag))
    
    
    def save_figures(self, outdir) :
        
        outname = "%s" %(self.label.replace("/", "_"))
        
        outpath = "%s/%s" %(outdir, outname)
        
        self.draw()
        
        self.fig_img.savefig("%s.pdf" %(outpath))
        self.fig_img.savefig("%s.png" %(outpath))
        
        self.on_fig_close(event = None)
