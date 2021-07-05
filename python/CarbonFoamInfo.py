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
import ProfileLine
import utils


class CarbonFoamInfo :
    
    def __init__(
        self,
        imgInfo,
        imgIdx,
        label,
        axis_profile,
        marker_profile,
    ) :
        
        self.imgInfo = imgInfo
        self.imgIdx = imgIdx
        self.label = label
        
        self.d_geomArtist = {}
        self.d_profileLine = {}
        
        self.d_drawnArtist = {}
        
        self.axis_profile = axis_profile
        self.marker_profile = marker_profile
        
        self.tkroot_img = None
        self.fig_img = None
        self.marker_img = None
        self.cid_marker = None
        
        self.event_startDrag = None
        self.l_cid_dragImg = []
    
    
    def resetAllArtists(self) :
        
        for key in self.d_geomArtist :
            
            utils.reset_artist(self.d_geomArtist[key])
    
    
    def add_geometryArtist(self, artist, label) :
        
        #print("Adding artist:", artist)
        
        self.d_geomArtist[label] = copy.copy(artist)
        utils.reset_artist(self.d_geomArtist[label])
    
    
    def add_profileLine(self, r1, c1, r2, c2, label) :
        
        self.d_profileLine[label] = ProfileLine.ProfileLine(
            r1, c1,
            r2, c2,
        )
    
    
    def on_fig_close(self, event) :
        
        if (self.fig_img == event.canvas.figure) :
            
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
    
    
    def get_profile(self, label) :
        
        rr = self.d_profileLine[label].rr
        cc = self.d_profileLine[label].cc
        
        nPix = len(rr)
        
        xx = []
        yy = []
        
        for iPix in range(nPix) :
            
            r = rr[iPix]
            c = cc[iPix]
            
            val = self.imgInfo.l_inputData[self.imgIdx][r, c]
            xx.append(iPix)
            yy.append(val)
            
            #print(rgb, val)
            
        
        xx = numpy.array(xx)
        yy = numpy.array(yy)
        
        return (xx, yy)
    
    
    def plot_profile(self, label, axis, color = "black", update = False) :
        
        if (label in self.d_drawnArtist and not update) :
            
            return
        
        xx, yy = self.get_profile(label = label)
        
        if (update) :
            
            self.d_drawnArtist[label].set_xdata(xx)
            self.d_drawnArtist[label].set_ydata(yy)
        
        else :
            
            self.d_drawnArtist[label] = axis.plot(xx, yy, color = color, linewidth = 2, label = label)[0]
            axis.legend()
        
        axis.relim()
        axis.autoscale_view()
        
        axis.figure.canvas.draw()
    
    
    def unplot_profile(self, label, axis) :
        
        if (label not in self.d_drawnArtist) :
            
            return
        
        self.d_drawnArtist[label].remove()
        del self.d_drawnArtist[label]
        #self.d_profileArtist[label] = None
        
        axis.legend()
        axis.figure.canvas.draw()
    
    
    def unplot_profiles(self, axis, draw = True) :
        
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
            "$\\bf{File\\ path:}$ %s" %(self.imgInfo.l_inputFileName[self.imgIdx]),
        )
        
        title.append(
            "$\\bf{File\\ name:}$ %s" %(self.imgInfo.l_inputFileName[self.imgIdx].split("/")[-1]),
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
            
            self.tkroot_img = tkinter.Toplevel()
            self.tkroot_img.wm_title(figName)
            
            self.fig_img = matplotlib.figure.Figure(figsize = [5, 5])
            self.fig_img.canvas = FigureCanvasTkAgg(self.fig_img, master = self.tkroot_img)
            
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
            self.cid_marker = self.fig_img.canvas.mpl_connect("motion_notify_event", self.animate_marker)
            
            self.axis_img = self.fig_img.add_subplot(1, 1, 1)
            self.axis_img.set_aspect("equal", "box")
            self.axis_img.set_xlim(self.imgInfo.l_imgExtent_pixelX[self.imgIdx])
            self.axis_img.set_ylim(self.imgInfo.l_imgExtent_pixelY[self.imgIdx][::-1])
            
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
            
            self.fig_img.colorbar(
                self.img,
                ax = self.axis_img,
                fraction = 0.046*(arr_inputImg.shape[0]/arr_inputImg.shape[1])
            )
            
            self.background = self.fig_img.canvas.copy_from_bbox(self.axis_img.get_figure().bbox)
            
            
            #for key in self.d_geomArtist :
            #    
            #    print(self.d_geomArtist[key].get_label(), self.d_geomArtist[key], self.d_geomArtist[key].get_visible(), self.d_geomArtist[key].get_figure())
            #    
            #    self.d_geomArtist[key].set_transform(self.axis_img.transData)
            
            self.drawGeomArtists()
            
            #for key in self.d_profileLine :
            #    
            #    #print("Pixels:", self.d_profileLine)
            #    print("Profile:", self.get_profile(key))
            
            
            # Buttons
            #self.axis_buttons = self.fig_img.add_axes([0.025, 0.025, 0.1, 0.03])
            #
            #self.button_reset = matplotlib.widgets.Button(self.axis_buttons, "Reset", color = "white", hovercolor = "lightgrey")
            #self.button_reset.on_clicked(self.reset)
            
            
            self.fig_img.tight_layout()
            
            self.marker_img = BlittedCursor.BlittedCursor_mod1(ax = self.axis_img)
            
            #matplotlib.pyplot.show(block = False)
            
            
            # Toolbar
            self.tbar_img = NavigationToolbar2Tk(self.fig_img.canvas, self.tkroot_img)
            self.tbar_img.update()
            self.fig_img.canvas.get_tk_widget().pack(side = tkinter.TOP, fill = tkinter.BOTH, expand = 1)
            
            self.button_show_allImages = tkinter.Button(master = self.tkroot_img, text = "Reset", takefocus = 0, command = self.reset)
            self.button_show_allImages.pack(side = tkinter.LEFT)
        
        else :
            
            #self.fig_img.canvas.manager.window.raise_()
            self.tkroot_img.lift()
    
    
    def animate_marker(self, event):
        
        #print("animate_marker:", event)
        
        if (event.inaxes is None) :
            
            return
        
        if (self.marker_img is None) :
            
            return
        
        if (self.marker_img.picked_artist is None or self.marker_img.draw_marker is None) :
            
            return
        
        label = self.marker_img.picked_artist.get_label()
        
        if (label not in self.d_drawnArtist or self.d_drawnArtist[label] is None) :
            
            return
        
        cx = self.marker_img.artist_marker.get_xdata()[0]
        cy = self.marker_img.artist_marker.get_ydata()[0]
        
        #cx, cy = self.marker_img.artist_marker.get_center()
        #cxTr, cyTr = (cx, cy)
        #cxTr, cyTr = self.axis_img.transAxes.inverted().transform((cx, cy))
        #cxTr, cyTr = self.axis_img.figure.transFigure.inverted().transform((cx, cy))
        
        xlim = self.imgInfo.l_imgExtent_pixelX[self.imgIdx]
        ylim = self.imgInfo.l_imgExtent_pixelY[self.imgIdx]
        
        cxTr = abs(cx - xlim[0]) / (xlim[1] - xlim[0])
        cyTr = abs(cy - ylim[0]) / (ylim[1] - ylim[0])
        
        #rpix = (1-cyTr)*self.imgInfo.nRow
        rpix = cyTr*self.imgInfo.nRow
        cpix = cxTr*self.imgInfo.nCol
        
        rr = self.d_profileLine[label].rr
        cc = self.d_profileLine[label].cc
        
        l_dist = [(rpix-pix[0])**2 + (cpix-pix[1])**2 for pix in zip(rr, cc)]
        #print(l_dist, min(l_dist))
        
        idx = l_dist.index(min(l_dist))
        #print(idx, self.d_drawnArtist[label].get_xdata())
        
        idx = numpy.argwhere(self.d_drawnArtist[label].get_xdata() == idx)
        idx = idx[0, 0] if idx.shape[0] else -1
        
        if (idx < 0) :
            
            return
        
        xval = self.d_drawnArtist[label].get_xdata()[idx]
        yval = self.d_drawnArtist[label].get_ydata()[idx]
        
        
        #print(
        #    label,
        #    (cx, cy),
        #    (event.x, event.y),
        #    (cxTr, cyTr),
        #    (rpix, cpix),
        #    (xval, yval),
        #)
        
        profx, profy = self.axis_profile.transData.transform_point([xval, yval])
        #profx, profy = self.axis_profile.transAxes.transform_point([xval, yval])
        #profx, profy = (xval, yval)
        
        #print("(xval, yval)", (xval, yval), "(profx, profy)", (profx, profy))
        
        self.marker_profile.on_mouse_move(
            matplotlib.backend_bases.MouseEvent(
                name = "evt",
                canvas = self.axis_profile.figure.canvas,
                x = profx,
                y = profy,
            ),
            xy = (xval, yval),
            draw_marker = True,
        )
    
    
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
    
    
    def on_pick(self, event) :
        
        artist = event.artist
        
        label = artist.get_label()
        print("Picked:", artist, label)
        
        label = label.split("_")[0]
        
        #self.imgInfo.on_mouse_click(event.mouseevent)
        
        event_key = str(event.mouseevent.key).lower()
        event_button = event.mouseevent.button
        
        clickX = event.mouseevent.xdata
        clickY = event.mouseevent.ydata
        
        print(event_key, event_button, clickX, clickY)
        
        #if (clickX is None or clickY is None) :
        #    
        #    return
        
        if (event_key == "shift" and event_button == matplotlib.backend_bases.MouseButton.LEFT) :
            
            self.draw()
            
            color = self.choose_color(l_skipColor = self.get_usedColors(axis = self.axis_profile, l_objectType = "Line2D"))
            
            self.plot_profile(
                label = artist.get_label(),
                axis = self.axis_profile,
                color = color,
            )
        
        elif (event_key == "shift" and event_button == matplotlib.backend_bases.MouseButton.RIGHT) :
            
            self.unplot_profile(
                label = artist.get_label(),
                axis = self.axis_profile,
            )
    
    
    def update_features(self, dRow, dCol) :
        
        for key in self.d_profileLine :
            
            rr, cc = self.d_profileLine[key].setAndGetLine(dRow = dRow, dCol = dCol)
            
            #arr_img = self.imgInfo.l_inputData[self.imgIdx].copy()
            #
            #arr_img[rr, cc] = -9999
            #
            #self.img.set_data(arr_img)
            
            if key in self.d_drawnArtist :
                
                self.plot_profile(
                    label = key,
                    axis = self.axis_profile,
                    update = True,
                )
    
    
    def update_imgExtent(self, new_extent, dX, dY) :
        
        #print(extent, "---->", new_extent, new_extent_mod)
        
        #self.fig_img.canvas.restore_region(self.background)
        
        self.img.set_extent(new_extent)
        
        self.axis_img.set_xlim(*new_extent[0: 2])
        self.axis_img.set_ylim(*new_extent[2: 4])
        
        self.fig_img._suptitle.set_text(self.get_title())
        
        #self.fig_img.canvas.update()
        self.fig_img.canvas.draw()
        #self.fig_img.canvas.blit(self.axis_img.bbox)
        
        #self.drawGeomArtists()
        
        #self.fig_img.canvas.blit(self.axis_img.clipbox)
        
        #self.fig_img.canvas.flush_events()
        
        self.imgInfo.updateImageExtent(idx = self.imgIdx, imgExtent_pixelX = new_extent[0: 2], imgExtent_pixelY = new_extent[2: 4][::-1])
        
        self.update_features(dY, dX)
    
    
    def reset(self) :
        
        dX, dY = self.imgInfo.resetImageExtent(idx = self.imgIdx)
        self.update_imgExtent(self.imgInfo.l_imgExtent_pixelX[self.imgIdx] + self.imgInfo.l_imgExtent_pixelY[self.imgIdx][::-1], dX, dY)
    
    
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
