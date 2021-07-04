import matplotlib
import numpy


# https://matplotlib.org/stable/gallery/misc/cursor_demo.html
class BlittedCursor:
    """
    A cross hair cursor using blitting for faster redraw.
    """
    def __init__(self, ax, background = None):
        self.ax = ax
        self.background = background
        self.horizontal_line = ax.axhline(color='k', lw=0.8, ls='--')
        self.vertical_line = ax.axvline(color='k', lw=0.8, ls='--')
        # text location in axes coordinates
        self.text = ax.text(0.72, 0.9, '', transform=ax.transAxes)
        self._creating_background = False
        ax.figure.canvas.mpl_connect('draw_event', self.on_draw)
        ax.figure.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)

    def on_draw(self, event):
        self.create_new_background()

    def set_cross_hair_visible(self, visible):
        need_redraw = self.horizontal_line.get_visible() != visible
        self.horizontal_line.set_visible(visible)
        self.vertical_line.set_visible(visible)
        self.text.set_visible(visible)
        return need_redraw

    def create_new_background(self):
        if self._creating_background:
            # discard calls triggered from within this function
            return
        self._creating_background = True
        self.set_cross_hair_visible(False)
        self.ax.figure.canvas.draw()
        self.background = self.ax.figure.canvas.copy_from_bbox(self.ax.bbox)
        self.set_cross_hair_visible(True)
        self._creating_background = False

    def on_mouse_move(self, event):
        if self.background is None:
            self.create_new_background()
        if not event.inaxes:
            need_redraw = self.set_cross_hair_visible(False)
            if need_redraw:
                self.ax.figure.canvas.restore_region(self.background)
                self.ax.figure.canvas.blit(self.ax.bbox)
        else:
            self.set_cross_hair_visible(True)
            # update the line positions
            x, y = event.xdata, event.ydata
            self.horizontal_line.set_ydata(y)
            self.vertical_line.set_xdata(x)
            self.text.set_text('x=%1.2f, y=%1.2f' % (x, y))

            self.ax.figure.canvas.restore_region(self.background)
            self.ax.draw_artist(self.horizontal_line)
            self.ax.draw_artist(self.vertical_line)
            #self.ax.draw_artist(self.text)
            self.ax.figure.canvas.blit(self.ax.bbox)



class BlittedCursor_mod1:
    """
    A cross hair cursor using blitting for faster redraw.
    """
    def __init__(self, ax, marker_size = 10):
        self.ax = ax
        self.background = None
        self.horizontal_line = ax.axhline(color="k", lw=0.8, ls="--")
        self.vertical_line = ax.axvline(color="k", lw=0.8, ls="--")
        # text location in axes coordinates
        #self.text = ax.text(0.72, 0.9, "", transform=ax.transAxes)
        self.text = ax.text(0.1, 0.1, "", transform=ax.transAxes, backgroundcolor = (1, 1, 1, 0.75))
        self._creating_background = False
        
        self.picked_artist = None
        self.artist_marker = None
        self.draw_marker = False
        
        #self.marker_width = marker_width
        #self.marker_height = marker_width
        #self.artist_marker = matplotlib.pyplot.Circle((0, 0), radius = self.marker_radius, color = "black", fill = False, transform = self.ax.transData)
        #self.artist_marker = matplotlib.patches.Ellipse((0, 0), width = self.marker_width, height = self.marker_height, color = "black", fill = False, transform = self.ax.transData)
        #self.artist_marker = matplotlib.patches.Ellipse((0, 0), width = 0.5, height = 0.5, color = "black", fill = False, transform = self.ax.transAxes)
        self.artist_marker = self.ax.add_artist(matplotlib.lines.Line2D([0], [0], marker = "o", markersize = marker_size, markeredgecolor = "k", markeredgewidth = 2, markerfacecolor = "none", animated = True))
        self.artist_marker.set_visible(False)
        
        self.line_slope = None
        self.line_intercept = None
        
        ax.figure.canvas.mpl_connect("draw_event", self.on_draw)
        ax.figure.canvas.mpl_connect("motion_notify_event", self.on_mouse_move)
        ax.figure.canvas.mpl_connect("pick_event", self.on_pick)
        ax.figure.canvas.mpl_connect("button_press_event", self.on_click)

    def on_draw(self, event):
        self.create_new_background()

    def set_cross_hair_visible(self, visible):
        need_redraw = self.horizontal_line.get_visible() != visible
        self.horizontal_line.set_visible(visible)
        self.vertical_line.set_visible(visible)
        self.text.set_visible(visible)
        return need_redraw

    def create_new_background(self):
        if self._creating_background:
            # discard calls triggered from within this function
            return
        self._creating_background = True
        self.set_cross_hair_visible(False)
        self.ax.figure.canvas.draw()
        self.background = self.ax.figure.canvas.copy_from_bbox(self.ax.bbox)
        self.set_cross_hair_visible(True)
        self._creating_background = False
    
    def interpLine(self, xy1, xy2, val, inv = False) :
        
        if (self.line_slope is None or self.line_intercept is None) :
            
            self.line_slope = (xy2[1] - xy1[1]) / (xy2[0] - xy1[0])
            self.line_intercept = xy1[1] - (self.line_slope*xy1[0])
        
        if (not inv) :
            
            return self.line_slope*val + self.line_intercept
        
        else :
            
            return (val-self.line_intercept)/self.line_slope
    
    def on_mouse_move(self, event, xy = None, draw_marker = False):
        
        marker_x = None
        marker_y = None
        artist_label = None
        self.draw_marker = draw_marker
        
        if self.background is None:
            self.create_new_background()
        if not event.inaxes:
            need_redraw = self.set_cross_hair_visible(False)
            if need_redraw:
                self.ax.figure.canvas.restore_region(self.background)
                self.ax.figure.canvas.blit(self.ax.bbox)
        else:
            self.set_cross_hair_visible(True)
            # update the line positions
            x, y = event.xdata, event.ydata
            self.horizontal_line.set_ydata(y)
            self.vertical_line.set_xdata(x)
            #self.text.set_text("Data x=%0.2f, y=%0.2f" % (x, y))
            
            marker_x = x
            marker_y = y
            
            if (self.picked_artist is not None) :
                
                if (isinstance(self.picked_artist, matplotlib.lines.Line2D)) :
                    
                    #print("Line2D")
                    
                    xx, yy = self.picked_artist.get_data(orig = True)
                    
                    #print("Line:", list(zip(xx, yy)))
                    
                    artist_label = self.picked_artist.get_label()
                    
                    if (min(xx) <= x <= max(xx)) :
                        
                        marker_y = self.interpLine(xy1 = [xx[0], yy[0]], xy2 = [xx[1], yy[1]], val = x)
                        
                        self.draw_marker = True
                    
                    elif (min(yy) <= y <= max(yy)) :
                        
                        marker_x = self.interpLine(xy1 = [xx[0], yy[0]], xy2 = [xx[1], yy[1]], val = y, inv = True)
                        
                        self.draw_marker = True
            
            
            
            #if (str(self.ax.get_aspect()) == "auto") :
            #    
            #    #self.artist_marker.set_width(self.marker_width)
            #    self.artist_marker.set_height(self.marker_height * abs(self.ax.get_ylim()[1] - self.ax.get_ylim()[0])/abs(self.ax.get_xlim()[1] - self.ax.get_xlim()[0]) * self.ax.figure.get_figwidth() / self.ax.figure.get_figheight())
            
            
            marker_center = (marker_x, marker_y)
            #self.artist_marker.set_center(marker_center)
            self.artist_marker.set_xdata([marker_x])
            self.artist_marker.set_ydata([marker_y])
            
            self.ax.figure.canvas.restore_region(self.background)
            self.ax.draw_artist(self.horizontal_line)
            self.ax.draw_artist(self.vertical_line)
            self.ax.draw_artist(self.text)
            
            #print((x, y), (marker_x, marker_y), self.draw_marker, self.ax.get_data_ratio())
            
            marker_text = ""
            
            if (self.draw_marker) :
                
                marker_text = "Marker x=%0.2f, y=%0.2f" % (marker_x, marker_y)
                
                self.artist_marker.set_visible(True)
                self.ax.draw_artist(self.artist_marker)
                
            
            self.text.set_text(marker_text)
            
            self.ax.figure.canvas.blit(self.ax.bbox)
    
    
    def on_pick(self, event) :
        
        if (event.mouseevent.key is not None) :
            
            return
        
        self.on_click(event.mouseevent, reset = True)
        
        self.picked_artist = event.artist
        
        #artist = event.artist
        #
        #label = artist.get_label()
        #print(artist, label)
        #
        #if (self.d_profileArtist[label] is None) :
        #    
        #    self.plot_profile(label = label)
        #
        #else :
        #    
        #    self.unplot_profile(label = label)
        #
        #
        #self.axis.legend()
        #self.fig.canvas.draw()
    
    
    def on_click(self, event, reset = False) :
        
        #button = event.button
        #print(button)
        
        if (reset or event.button == matplotlib.backend_bases.MouseButton.RIGHT) :
            
            self.picked_artist = None
            self.line_slope = None
            self.line_intercept = None
            
            #self.artist_marker.set_xdata([0])
            #self.artist_marker.set_ydata([0])
            self.artist_marker.set_visible(False)
