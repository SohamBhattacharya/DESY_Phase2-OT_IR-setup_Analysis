import argparse
import collections
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
import os
import pandas
import PIL
import re
import scipy
import scipy.fft
import scipy.signal
import skimage
import skimage.draw
import skimage.measure
import sortedcontainers
import sys
import textwrap
import time
import tkinter
import yaml

matplotlib.pyplot.rcParams["text.usetex"] = True
matplotlib.pyplot.rcParams["text.latex.preamble"] = r"\usepackage{amsmath} \usepackage{commath}"

#import ROOT
#ROOT.gROOT.SetBatch(1)

import constants
import colors
import utils


def main() :
    
    # Argument parser
    parser = argparse.ArgumentParser(formatter_class = argparse.ArgumentDefaultsHelpFormatter)
    
    parser.add_argument(
        "--coolYml",
        help = "The yml file with the cooling circuit temperatures",
        type = str,
        required = True,
    )
    
    parser.add_argument(
        "--coolXls",
        help = "The xls file containing the insert distances along the cooling circuits",
        type = str,
        required = True,
    )
    
    parser.add_argument(
        "--skipCircuits",
        help = "Lists of circuits to skip. For e.g. circuit_3h",
        type = str,
        nargs = "*",
        required = False,
        default = [],
    )
    
    parser.add_argument(
        "--skipInsertsInFit",
        help = "Lists of inserts to omit in the fit. For e.g. R13/2S1_ins3 R15/2S1_ins1 ",
        type = str,
        nargs = "*",
        required = False,
        default = [],
    )
    
    parser.add_argument(
        "--side",
        help = "Side",
        type = str,
        required = True,
        choices = [constants.side_top_str, constants.side_bottom_str],
    )
    
    parser.add_argument(
        "--yRangeDeltaT",
        help = "Y-axis range for the deltaT plots: lower upper",
        type = float,
        nargs = 2,
        required = False,
        default = [-3.0, 3.0],
    )
    
    parser.add_argument(
        "--outdir",
        help = "Output directory",
        type = str,
        required = False,
        default = "tmp/analyze_2Smodules",
    )
    
    parser.add_argument(
        "--title",
        help = "Title to be added to plots",
        type = str,
        required = False,
        default = "",
    )
    
    
    args = parser.parse_args()
    d_args = vars(args)
    
    l_marker = ["o", "s", "^", "v", "D", "<", ">"]
    
    title_latex = args.title
    title_latex = title_latex.replace("_", "\_")
    
    outdir = args.outdir
    os.system("mkdir -p %s" %(outdir))
    
    print("Loading data from: %s" %(args.coolYml))
    
    d_coolCircTemp = utils.load_yaml(args.coolYml)
    print(d_coolCircTemp.keys())
    #print(d_coolCircTemp)
    
    df_coolCircXls = utils.load_xls(args.coolXls)
    #print(df_coolCircXls)
    
    l_circuit = utils.naturalsort(list(d_coolCircTemp.keys()))
    
    #insertLabel_pattern_regex = "R(\d+)/2S(\d+)_ins(\d+)"
    insertLabel_pattern_regex = "ins(\d+)"
    
    d_module_deltaT = sortedcontainers.SortedDict()
    
    fig_module_deltaT = matplotlib.figure.Figure(figsize = [10, 8])
    axis_module_deltaT = fig_module_deltaT.add_subplot(1, 1, 1)
    
    fig_module_insertDeltaT = matplotlib.figure.Figure(figsize = [10, 8])
    axis_module_insertDeltaT = fig_module_insertDeltaT.add_subplot(1, 1, 1)
    
    fig_test1 = matplotlib.figure.Figure(figsize = [10, 8])
    axis_test1 = fig_test1.add_subplot(1, 1, 1)
    
    l_circuitHandle = []
    l_circuitLabel = []
    
    for iCircuit, circuit in enumerate(l_circuit) :
        
        fig_circuitTemp = matplotlib.figure.Figure(figsize = [10, 8])
        axis_circuitTemp = fig_circuitTemp.add_subplot(1, 1, 1)
        
        if (circuit not in df_coolCircXls) :
            
            print(f"Did not find {circuit} in xls file.")
            continue
        
        
        #print(circuit)
        
        columnHeading_side = "%s.2" %(circuit)
        columnHeading_dist = "%s.3" %(circuit)
        
        #print(list(zip(d_coolCircTemp[circuit], list(df_coolCircXls[columnHeading_dist])[1:])))
        
        a_insertLabel = numpy.array([list(_d.keys())[0] for _d in d_coolCircTemp[circuit]], dtype = str)
        a_insertTemp  = numpy.array([list(_d.values())[0] for _d in d_coolCircTemp[circuit]])
        
        #print(a_insertLabel)
        
        a_insertTemp_isfinite = numpy.isfinite(a_insertTemp)
        
        # Set the skip inserts
        l_skipInsertPos = [_idx for (_idx, _val) in enumerate(a_insertLabel) if _val in args.skipInsertsInFit]
        a_insertTemp_isfinite[l_skipInsertPos] = False
        
        a_insertDist = list(df_coolCircXls[columnHeading_dist])[1:]
        a_insertDist = a_insertDist[0: len(a_insertLabel)]
        a_insertDist = numpy.cumsum(a_insertDist)
        
        a_insertSide = numpy.array(list(df_coolCircXls[columnHeading_side])[1:], dtype = str)
        
        #print(list(zip(a_insertLabel, a_insertTemp, a_insertDist)))
        
        fitFunc = lambda x, p0, p1: p0 + p1*x
        
        fitParVals, fitParCovs = scipy.optimize.curve_fit(
            f = fitFunc,
            xdata = a_insertDist[a_insertTemp_isfinite],
            ydata = a_insertTemp[a_insertTemp_isfinite],
            #check_finite = False,
        )
        
        fitParErrs = numpy.sqrt(numpy.diag(fitParCovs))
        fitLabel = "y = (%0.4g±%0.4g) + (%0.4g±%0.4g)x" %(fitParVals[0], fitParErrs[0], fitParVals[1], fitParErrs[1])
        print(fitLabel)
        
        fit_intercept = fitParVals[0]
        fit_slope = fitParVals[1]
        
        xx_fitLine = [a_insertDist[0], a_insertDist[-1]]
        yy_fitLine = [fitFunc(_x, *fitParVals) for _x in xx_fitLine]
        
        axis_circuitTemp.plot(
            xx_fitLine,
            yy_fitLine,
            "-",
            markersize = 0,
            color = "blue",
            label = fitLabel,
        )
        
        #print("%s:\t\t p0 = %+0.4f±%0.4f, p1 = %+0.4f±%0.4f" %(self.label, self.fitParVals[0], self.fitParErrs[0], self.fitParVals[1], self.fitParErrs[1]))
        
        l_prev_dTdL = [0]*4
        l_prev_dTdL_count = [0]*4
        
        for idx in range(len(a_insertTemp)) :
            
            same_side = (args.side == a_insertSide[idx])
            
            marker = "o"
            color = "blue"
            fillstyle = "full"
            x = a_insertDist[idx]
            y = a_insertTemp[idx]
            
            moduleLabel = a_insertLabel[idx].split("_")[0]
            insertLabel = a_insertLabel[idx].split("_")[1]
            
            if (same_side and moduleLabel not in d_module_deltaT) :
                
                d_module_deltaT[moduleLabel] = sortedcontainers.SortedDict()
            
            if (same_side and a_insertLabel[idx] in args.skipInsertsInFit) :
                
                color = "skyblue"
            
            if (circuit not in args.skipCircuits) :
                
                if (not numpy.isfinite(y)) :
                    
                    marker = "o"
                    color = "grey"
                    fillstyle = "none"
                    
                    #y = 0
                    y = fitFunc(x, *fitParVals)
                
                axis_circuitTemp.plot(x, y, color = color, linestyle = "", marker = marker, fillstyle = fillstyle)
                
                if (same_side) :
                    
                    deltaT = y - fitFunc(x, *fitParVals)
                    d_module_deltaT[moduleLabel][insertLabel] = deltaT
                    
                    axis_circuitTemp.annotate(
                        "\\textbf{%s}" %(a_insertLabel[idx].replace("_", "\_")),
                        xy = (x, y),
                        xycoords = "data",
                        xytext = (0, -5),
                        textcoords = "offset points",
                        rotation = 90,
                        horizontalalignment = "center",
                        verticalalignment = "top",
                        fontsize = "small",
                        weight = "bold",
                    )
                    
                    deltaX_prev_oppSide = None
                    deltaT_prev_oppSide = None
                    
                    #if (fit_slope > 0 and idx > 0 and args.side != a_insertSide[idx-1]) :
                    #    
                    #    deltaX_prev_oppSide = a_insertDist[idx] - a_insertDist[idx-1]
                    #    deltaT_prev_oppSide = a_insertTemp[idx] - fitFunc(a_insertDist[idx-1], *fitParVals)
                    #
                    #elif (fit_slope < 0 and idx < len(a_insertTemp)-1 and args.side != a_insertSide[idx+1]) :
                    #    
                    #    deltaX_prev_oppSide = a_insertDist[idx] - a_insertDist[idx+1]
                    #    deltaT_prev_oppSide = a_insertTemp[idx] - fitFunc(a_insertDist[idx+1], *fitParVals)
                    #
                    #if (deltaX_prev_oppSide is not None and deltaT_prev_oppSide is not None) :
                    #    
                    #    axis_test1.plot(
                    #        abs(deltaX_prev_oppSide),
                    #        deltaT_prev_oppSide,
                    #        color = colors.highContrastColors_2[iCircuit],
                    #        linestyle = "",
                    #        marker = "o",
                    #        fillstyle = "none",
                    #    )
                    
                    #itr = -1 if (fit_slope > 0) else +1
                    itr = -1 if (fitFunc(a_insertDist[-1], *fitParVals) > fitFunc(a_insertDist[0], *fitParVals)) else +1
                    
                    idx_prev_sameSide = idx
                    foundInsSameSide = False
                    
                    while(True) :
                        
                        if (itr == -1 and idx_prev_sameSide == 0) :
                            
                            break
                        
                        if (itr == +1 and idx_prev_sameSide == len(a_insertTemp)-1) :
                            
                            break
                        
                        idx_prev_sameSide += itr
                        
                        if (args.side == a_insertSide[idx_prev_sameSide]) :
                            
                            foundInsSameSide = True
                            break
                    
                    if (idx_prev_sameSide != idx and foundInsSameSide) :
                        
                        prevCount = abs(idx_prev_sameSide-idx)-1
                        
                        #x_tmp = prevCount
                        #x_tmp = abs(a_insertDist[idx] - a_insertDist[idx_prev_sameSide])
                        #y_tmp = a_insertTemp[idx] - a_insertTemp[idx_prev_sameSide]
                        #
                        #x_tmp = x_tmp/prevCount if (prevCount) else 0
                        
                        x_tmp = prevCount
                        y_tmp = (a_insertTemp[idx] - a_insertTemp[idx_prev_sameSide]) / abs(a_insertDist[idx] - a_insertDist[idx_prev_sameSide])
                        
                        if (numpy.isnan(y_tmp)) :
                            
                            #print("nan", circuit, a_insertLabel[idx], a_insertTemp[idx], a_insertTemp[idx_prev_sameSide], a_insertDist[idx], a_insertDist[idx_prev_sameSide])
                            print("nan", circuit, a_insertLabel[idx], a_insertTemp[idx], a_insertLabel[idx_prev_sameSide], a_insertTemp[idx_prev_sameSide])
                        
                        l_prev_dTdL[prevCount] += y_tmp
                        l_prev_dTdL_count[prevCount] += 1
                        
                        artist = axis_test1.plot(
                            x_tmp,
                            y_tmp,
                            color = colors.highContrastColors_1[iCircuit],
                            linestyle = "",
                            marker = "o",
                            fillstyle = "none",
                        )[0]
                        
                        circuitLabel = circuit.replace("_", "\_")
                        
                        if (circuitLabel not in l_circuitLabel) :
                            
                            l_circuitHandle.append(artist)
                            l_circuitLabel.append(circuitLabel)
                        
                        #print(x_tmp, y_tmp, prevCount)
                
        
        #l_prev_dTdL = [(float(_num)/_den) if _den for _num, _den in zip(l_prev_dTdL, l_prev_dTdL_count) else None]
        
        l_prev_dTdL_avg = []
        
        for _num, _den in zip(l_prev_dTdL, l_prev_dTdL_count) :
            
            if (_den) :
                
                l_prev_dTdL_avg.append(_num/_den)
            
            else :
                
                l_prev_dTdL_avg.append(numpy.nan)
        
        print(circuit, l_prev_dTdL_avg)
        
        axis_test1.plot(
            list(range(0, len(l_prev_dTdL_avg))),
            l_prev_dTdL_avg,
            color = colors.highContrastColors_1[iCircuit],
            linestyle = "--",
            marker = "*",
            markersize = 15,
            #fillstyle = "full",
            fillstyle = "none",
        )
        
        
        #axis_circuitTemp.set_xlim(-3, len(l_cfoam_label_sorted)+1)
        #axis_circuitTemp.set_ylim(0, 3.0)
        axis_circuitTemp.set_xlabel("Position along circuit [mm]", fontsize = 20)
        axis_circuitTemp.set_ylabel("Temperature [{\\textdegree}C]", fontsize = 20)
        axis_circuitTemp.tick_params(axis = "both", labelsize = 20)
        axis_circuitTemp.set_title("%s (%s)" %(title_latex, circuit.replace("_", "\_")), fontsize = 20)
        axis_circuitTemp.figure.tight_layout()
        axis_circuitTemp.figure.savefig("%s/%s.pdf" %(outdir, circuit))
        axis_circuitTemp.figure.savefig("%s/%s.png" %(outdir, circuit))
        matplotlib.pyplot.close(fig_circuitTemp)
    
    print("d_module_deltaT:")
    print(d_module_deltaT)
    
    
    l_label = []
    l_moduleLabel_sorted = utils.naturalsort(list(d_module_deltaT.keys()))
    l_xtick_label = ["\\textbf{%s}" %(_ele.replace("_", "\_")) for _ele in l_moduleLabel_sorted]
    xx_module_deltaT = list(range(len(d_module_deltaT)))
    
    
    l_insertHandle = []
    l_insertHandleLabel = []
    
    for moduleIdx, moduleLabel in enumerate(l_moduleLabel_sorted) :
        
        l_insertLabel_sorted = utils.naturalsort(list(d_module_deltaT[moduleLabel].keys()))
        
        for insertIdx, insertLabel in enumerate(l_insertLabel_sorted) :
            
            insertNumber = int(re.findall(insertLabel_pattern_regex, insertLabel)[0])
            #print(insertNumber)
            
            artist = axis_module_insertDeltaT.plot(
                moduleIdx,
                d_module_deltaT[moduleLabel][insertLabel],
                color = colors.highContrastColors_2[insertNumber-1],
                linestyle = "",
                marker = l_marker[insertNumber-1],
                markersize = 7,
                label = insertLabel,
                fillstyle = "none",
            )[0]
            
            if (insertLabel not in l_insertHandleLabel) :
                
                l_insertHandle.append(artist)
                l_insertHandleLabel.append(insertLabel)
                
                print(moduleLabel, insertLabel, artist)
    
    
    yy_module_deltaT = [numpy.mean(d_module_deltaT[_key].values()) for _key in l_moduleLabel_sorted]
    #yy_module_deltaT = [numpy.mean(numpy.abs(d_module_deltaT[_key].values())) for _key in l_xtick_label]
    label = "$\\langle \\Delta T_\\text{ins} \\rangle$"
    l_label.append(label)
    plot_ret = axis_module_deltaT.plot(
        xx_module_deltaT,
        yy_module_deltaT,
        color = colors.highContrastColors_2[len(l_label)-1],
        linestyle = "",
        marker = l_marker[len(l_label)-1],
        markersize = 7,
        label = label,
    )
    
    utils.clip_and_plot_outliers_y(
        ax = axis_module_deltaT,
        xx = xx_module_deltaT,
        yy = yy_module_deltaT,
        yMin = args.yRangeDeltaT[0], yMax = args.yRangeDeltaT[1],
        d_plotOpt = {
            "color": plot_ret[0].get_color(),
            "linestyle": "",
            "fillstyle": "full",
            "markersize": 7,
            "clip_on": False,
        },
    )
    
    
    #yy_module_deltaT = [numpy.max(numpy.abs(d_module_deltaT[_key].values())) if len(d_module_deltaT[_key].values()) else 0 for _key in l_moduleLabel_sorted]
    yy_module_deltaT = [numpy.mean(numpy.abs(d_module_deltaT[_key].values())) for _key in l_moduleLabel_sorted]
    label = "$\\langle \\abs{\\Delta T_\\text{ins}} \\rangle$"
    l_label.append(label)
    plot_ret = axis_module_deltaT.plot(
        xx_module_deltaT,
        yy_module_deltaT,
        color = colors.highContrastColors_2[len(l_label)-1],
        linestyle = "",
        marker = l_marker[len(l_label)-1],
        markersize = 7,
        label = label,
    )
    
    #utils.clip_and_plot_outliers_y(
    #    ax = axis_module_deltaT,
    #    xx = xx_module_deltaT,
    #    yy = yy_module_deltaT,
    #    yMin = args.yRangeDeltaT[0], yMax = args.yRangeDeltaT[1],
    #    d_plotOpt = {
    #        "color": plot_ret[0].get_color(),
    #        "linestyle": "",
    #        "fillstyle": "full",
    #        "markersize": 7,
    #        "clip_on": False,
    #    },
    #)
    
    
    
    axis_module_insertDeltaT.set_xlim(-2, len(l_moduleLabel_sorted)+1)
    axis_module_insertDeltaT.set_ylim(*args.yRangeDeltaT)
    axis_module_insertDeltaT.set_ylabel("[{\\textdegree}C]", fontsize = 20)
    axis_module_insertDeltaT.set_xticks(xx_module_deltaT)#, l_xtick_label, fontsize = "xx-small", rotation = 45)
    axis_module_insertDeltaT.set_xticklabels(l_xtick_label, fontsize = "large", rotation = 90, weight = "bold")
    axis_module_insertDeltaT.tick_params(axis = "y", labelsize = 20)
    axis_module_insertDeltaT.grid(visible = True, which = "major", axis = "both", linestyle = "--")
    axis_module_insertDeltaT.legend(l_insertHandle, l_insertHandleLabel, fontsize = 20, ncol = 2)
    axis_module_insertDeltaT.set_title(title_latex, fontsize = 20)
    axis_module_insertDeltaT.figure.tight_layout()
    axis_module_insertDeltaT.figure.savefig("%s/module_insertDeltaT.pdf" %(outdir))
    axis_module_insertDeltaT.figure.savefig("%s/module_insertDeltaT.png" %(outdir))
    matplotlib.pyplot.close(fig_module_insertDeltaT)
    
    
    axis_module_deltaT.set_xlim(-2, len(xx_module_deltaT)+1)
    axis_module_deltaT.set_ylim(*args.yRangeDeltaT)
    axis_module_deltaT.set_ylabel("[{\\textdegree}C]", fontsize = 20)
    axis_module_deltaT.set_xticks(xx_module_deltaT)#, l_xtick_label, fontsize = "xx-small", rotation = 45)
    axis_module_deltaT.set_xticklabels(l_xtick_label, fontsize = "large", rotation = 90, weight = "bold")
    axis_module_deltaT.tick_params(axis = "y", labelsize = 20)
    axis_module_deltaT.grid(visible = True, which = "major", axis = "both", linestyle = "--")
    handles_, labels_ = axis_module_deltaT.get_legend_handles_labels()
    handles = [handles_[labels_.index(_ele)] for _ele in l_label]
    axis_module_deltaT.legend(handles, l_label, fontsize = 20)
    axis_module_deltaT.set_title(title_latex, fontsize = 20)
    axis_module_deltaT.figure.tight_layout()
    axis_module_deltaT.figure.savefig("%s/module_deltaT.pdf" %(outdir))
    axis_module_deltaT.figure.savefig("%s/module_deltaT.png" %(outdir))
    matplotlib.pyplot.close(fig_module_deltaT)
    
    
    #axis_test1.set_xlim(0, 200)
    axis_test1.set_xlabel("\# opposite-side inserts b/w inserts $i$ and $i-1$", fontsize = 20)
    #axis_test1.set_ylabel("$\\frac{T_i - T_{i-1}}{\\abs{l_i - l_{i-1}}}$ [{\\textdegree}C/mm]", fontsize = 20)
    #axis_test1.set_ylabel("$(T_i - T_{i-1}) / \\abs{l_i - l_{i-1}}$ [{\\textdegree}C/mm]", fontsize = 20)
    axis_test1.set_ylabel("$(T_i - T_{i-1}) / \\Delta L_{i,\ i-1}$ [{\\textdegree}C/mm]", fontsize = 20)
    axis_test1.tick_params(axis = "x", labelsize = 20)
    axis_test1.tick_params(axis = "y", labelsize = 20)
    axis_test1.set_xticks(list(range(0, 5)))
    axis_test1.legend(l_circuitHandle, l_circuitLabel, fontsize = 20, ncol = 2)
    axis_test1.set_title(title_latex, fontsize = 20)
    axis_test1.figure.tight_layout()
    axis_test1.figure.savefig("%s/test1.pdf" %(outdir))
    axis_test1.figure.savefig("%s/test1.png" %(outdir))
    matplotlib.pyplot.close(fig_test1)



if (__name__ == "__main__") :
    
    main()
