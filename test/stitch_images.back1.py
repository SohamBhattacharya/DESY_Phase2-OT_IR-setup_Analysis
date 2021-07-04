import argparse
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
import time


def motor_stepX_to_mm(step) :
    
    return step * 1920.0/34952


def motor_stepY_to_mm(step) :
    
    return step * 895.0/716059


def mm_to_pix(l) :
    
    return l * 319/55.26


def motor_stepX_to_pix(step) :
    
    return mm_to_pix(motor_stepX_to_mm(step))


def motor_stepY_to_pix(step) :
    
    return mm_to_pix(motor_stepY_to_mm(step))


class ImageInfo :
    
    def __init__(
        self,
        args,
    ) :
        
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
                #dtype = numpy.float16,
                dtype = numpy.float,
                delimiter = "\t",
                skiprows = 9,
                usecols = list(range(0, args.nCol)),
                encoding = args.inputEncoding,
            ))
        
        
        self.nRow = self.l_inputData[0].shape[0]
        self.nCol = self.l_inputData[0].shape[1]
        
        assert (self.nCol == args.nCol), "Mismatch in given (%d) and encountered (%d) value of \"nCol\"" %(args.nCol, self.nCol)
        
        self.min_motorX = min(self.l_motorX)
        self.max_motorX = max(self.l_motorX)
        
        self.min_motorY = min(self.l_motorY)
        self.max_motorY = max(self.l_motorY)
        
        self.widthX_motor = self.max_motorX - self.min_motorX
        self.widthY_motor = self.max_motorY - self.min_motorY
        
        self.widthX_pix = int(motor_stepX_to_pix(self.widthX_motor) + self.nCol)
        self.widthY_pix = int(motor_stepY_to_pix(self.widthY_motor) + self.nRow)
        
        #print(min(l_motorX), max(l_motorX), max(l_motorX)-min(l_motorX))
        #print(min(l_motorY), max(l_motorY), max(l_motorY)-min(l_motorY))
        
        #print(
        #    "min_motorX %f, max_motorX %f, widthX_motor %f, widthX_pix %f, "
        #    
        #%(
        #    min_motorX, max_motorX, widthX_motor, widthX_pix,
        #))
        #
        #print(
        #    "min_motorY %f, max_motorY %f, widthY_motor %f, widthY_pix %f, "
        #    
        #%(
        #    min_motorY, max_motorY, widthY_motor, widthY_pix,
        #))
        
        #print(l_inputData[0].shape)
        #print(l_inputData[50].shape)
        
        
        self.arr_stitchedDeeImg = numpy.full((self.widthY_pix, self.widthX_pix), fill_value = -9999, dtype = numpy.float)#, dtype = numpy.float16)
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
            
            pixelX_lwr = int(motor_stepX_to_pix(motorX))
            pixelY_lwr = int(motor_stepY_to_pix(motorY))
            
            pixelX_upr = pixelX_lwr + self.nCol
            pixelY_upr = pixelY_lwr + self.nRow
            
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
            
            
            self.minTemp = arr_img.min() if (arr_img.min() < self.minTemp) else self.minTemp
            self.maxTemp = arr_img.max() if (arr_img.max() > self.maxTemp) else self.maxTemp
        
        
        self.l_fig_inputImg = [None] * len(self.l_inputData)
        
        
        self.colormap = matplotlib.cm.get_cmap("nipy_spectral").copy()
        self.colormap.set_under(color = "w")
    
    
    def getNearestImageIdx(self, pixelX, pixelY) :
        
        minDist2 = sys.float_info.max
        nearestIdx = -1
        
        for idx, (imgX, imgY) in enumerate(zip(self.l_imgCenter_pixelX, self.l_imgCenter_pixelY)) :
            
            dist2 = (imgX-pixelX)**2 + (imgY-pixelY)**2
            
            if (dist2 < minDist2) :
                
                minDist2 = dist2
                nearestIdx = idx
        
        
        return nearestIdx
    
    
    def on_inputImage_close(self, event) :
        
        print(event.name, event.canvas, event.canvas.figure)
        
        for iImg in range(0, len(self.l_fig_inputImg)) :
            
            if (self.l_fig_inputImg[iImg] == event.canvas.figure) :
                
                self.l_fig_inputImg[iImg].clf()
                matplotlib.pyplot.close(self.l_fig_inputImg[iImg])
                
                for axis in self.l_fig_inputImg[iImg].get_axes() :
                    
                    axis.clf()
                    axis.remove()
                
                self.l_fig_inputImg[iImg] = None
                
                gc.collect()
                
                print("Closed image id %d." %(iImg))
    
    
    def on_mouse_click(self, event) :
        
        event_key = str(event.key).lower()
        event_button = event.button
        
        clickX = event.xdata
        clickY = event.ydata
        
        print(event_key, event_button, clickX, clickY)
        
        if (clickX is None or clickY is None) :
            
            return
            
        
        if ("shift" in event_key and event_button == matplotlib.backend_bases.MouseButton.LEFT) :
            
            imgIdx = self.getNearestImageIdx(clickX, clickY)
            
            print("imgIdx:", imgIdx)
            
            if (self.l_fig_inputImg[imgIdx] is None) :
                
                figName = "Input image idx %d" %(imgIdx)
                
                self.l_fig_inputImg[imgIdx] = matplotlib.pyplot.figure(figName, figsize = [5, 3])
                
                self.l_fig_inputImg[imgIdx].canvas.mpl_connect("close_event", self.on_inputImage_close)
                
                axis_inputImg = self.l_fig_inputImg[imgIdx].add_subplot(1, 1, 1)
                axis_inputImg.set_aspect("equal", "box")
                
                arr_inputImg = self.l_inputData[imgIdx]
                
                img = axis_inputImg.imshow(
                    arr_inputImg,
                    origin = "upper",
                    extent = self.l_imgExtent_pixelX[imgIdx]+self.l_imgExtent_pixelY[imgIdx][::-1],
                    cmap = self.colormap,
                    vmin = self.minTemp,
                    vmax = 10,#maxTemp,
                )
                
                self.l_fig_inputImg[imgIdx].colorbar(
                    img,
                    ax = axis_inputImg,
                    fraction = 0.046*(arr_inputImg.shape[0]/arr_inputImg.shape[1])
                )
                
                self.l_fig_inputImg[imgIdx].tight_layout()
                
                #fig_stitchedDee.show()
                
                #matplotlib.pyplot.draw()
                
                #fig_inputImg.canvas.show()
                #print("Drawn new figure.")
                
                matplotlib.pyplot.show(block = False)
            
            else :
                
                self.l_fig_inputImg[imgIdx].canvas.manager.window.raise_()
    
    
    def run(self) :
        
        self.fig_stitchedDee = matplotlib.pyplot.figure(
            "Stitched image",
            figsize = [10, 8]
        )
        
        self.fig_stitchedDee.canvas.mpl_connect("button_press_event", self.on_mouse_click)
        
        self.axis_stitchedDee = self.fig_stitchedDee.add_subplot(1, 1, 1)
        self.axis_stitchedDee.set_aspect("equal", "box")
        
        img = self.axis_stitchedDee.imshow(
            self.arr_stitchedDeeImg,
            #norm = matplotlib.colors.LogNorm(vmin = 1e-6, vmax = 1.0),
            #norm = matplotlib.colors.Normalize(vmin = minTemp, vmax = maxTemp, clip = False),
            origin = "upper",
            cmap = self.colormap,
            vmin = self.minTemp,
            vmax = 10,#maxTemp,
        )
        
        self.fig_stitchedDee.colorbar(
            img,
            ax = self.axis_stitchedDee,
            fraction = 0.046*(self.arr_stitchedDeeImg.shape[0]/self.arr_stitchedDeeImg.shape[1])
        )
        
        self.fig_stitchedDee.tight_layout()
        
        #fig_stitchedDee.show()
        
        self.fig_stitchedDee.canvas.draw()
        
        #matplotlib.pyplot.show()


def main() :
    
    # Argument parser
    parser = argparse.ArgumentParser(formatter_class = argparse.RawTextHelpFormatter)
    
    parser.add_argument(
        "--inputDir",
        help = "Location of the input files",
        type = str,
        required = True,
    )
    
    parser.add_argument(
        "--inputPattern",
        help = "Input file name pattern (use XXX and YYY as the coordinate placeholders): image_XXX_YYY.asc",
        type = str,
        required = False,
        default = "cfoam_m20deg_lampoff_XXX_YYY.asc",
    )
    
    parser.add_argument(
        "--inputExt",
        help = "Input file extension",
        type = str,
        required = False,
        default = ".asc",
    )
    
    parser.add_argument(
        "--inputEncoding",
        help = "Input file encoding",
        type = str,
        required = False,
        default = "ISO-8859-1",
    )
    
    parser.add_argument(
        "--nCol",
        help = "Number of columns (the trailing delimeter causes problems, so specify this to avoid that)",
        type = int,
        required = False,
        default = 1024,
    )
    
    
    args = parser.parse_args()
    d_args = vars(args)
    
    
    imgInfo = ImageInfo(args = args)
    
    
    #fig = matplotlib.pyplot.figure(figsize = [10, 8])
    #
    #axis = fig.add_subplot(1, 1, 1)
    #axis.set_aspect("equal", "box")
    #
    #colormap = matplotlib.cm.get_cmap("nipy_spectral").copy()
    #colormap.set_under(color = "w")
    #
    #img = axis.imshow(
    #    imgInfo.arr_stitchedDeeImg,
    #    #norm = matplotlib.colors.LogNorm(vmin = 1e-6, vmax = 1.0),
    #    #norm = matplotlib.colors.Normalize(vmin = minTemp, vmax = maxTemp, clip = False),
    #    origin = "upper",
    #    cmap = colormap,
    #    vmin = imgInfo.minTemp,
    #    vmax = 10,#maxTemp,
    #)
    #
    #fig.colorbar(img, ax = axis)
    #
    #fig.tight_layout()
    #
    ##fig.show()
    
    
    imgInfo.run()
    
    
    #matplotlib.pyplot.draw()
    matplotlib.pyplot.show()
    
    #time.sleep(10000)
    
    
    
    
    
    return 0


if (__name__ == "__main__") :
    
    main()
