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
import sys
import textwrap
import time
import tkinter
import yaml

matplotlib.pyplot.rcParams["text.usetex"] = True
matplotlib.pyplot.rcParams["text.latex.preamble"] = r"\usepackage{amsmath}"

import ROOT
ROOT.gROOT.SetBatch(1)

import constants
import colors
import utils


def main() :
    
    # Argument parser
    parser = argparse.ArgumentParser(formatter_class = argparse.RawTextHelpFormatter)
    
    parser.add_argument(
        "--datayml",
        help = "The yml file with the data",
        type = str,
        required = True,
    )
    
    parser.add_argument(
        "--skipCfoams",
        help = "List of cfoams to skip. E.g. \"R1/CF10\" \"R5/CF14\" ...",
        type = str,
        nargs = "*",
        required = False,
        default = [],
    )
    
    parser.add_argument(
        "--lyonDTfile",
        help = "Lyon DeltaT file",
        type = str,
        required = False,
        default = None,
    )
    
    parser.add_argument(
        "--outdir",
        help = "Output directory",
        type = str,
        required = False,
        default = "tmp/analyze_profiles",
    )
    
    parser.add_argument(
        "--side",
        help = "Side",
        type = str,
        required = True,
        choices = [constants.side_top_str, constants.side_bottom_str],
    )
    
    parser.add_argument(
        "--nSegExc",
        help = (
            "Number of segments to divide the profile into; (optionally) followed by which segments (index) to exclude. \n"
            "E.g. \"3\" will create 3 segments and exclude none."
            "E.g. \"5 0 4\" will create 5 segments and exclude the 1st and 4th."
        ),
        type = int,
        nargs = "*",
        required = False,
        default = [5, 0, 4],
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
    
    
    outdir = args.outdir
    os.system("mkdir -p %s" %(outdir))
    
    #loadFileName = "plots/Lyon_dee_no-connector_side_cfoams_lamp_off_2021-11-11/profiles.yml"
    loadFileName = args.datayml
    print("Loading data from: %s" %(loadFileName))
    
    d_profileData = {}
    
    with open(loadFileName, "r") as fopen :
        
        d_profileData = yaml.load(fopen.read(), Loader = yaml.FullLoader)
    
    #cfoam_label = "R9/CF11"
    
    nSegment = args.nSegExc[0]
    
    l_marker = ["o", "s", "^", "v", "D", "<", ">"]
    
    l_xtick = []
    l_xtick_label = []
    
    l_cfoam_label_sorted = utils.naturalsort(d_profileData.keys())
    
    fig_deltaT = matplotlib.figure.Figure(figsize = [10, 8])
    axis_deltaT = fig_deltaT.add_subplot(1, 1, 1)
    
    fig_profile_stdDev = matplotlib.figure.Figure(figsize = [10, 8])
    axis_profile_stdDev_mean = fig_profile_stdDev.add_subplot(1, 1, 1)
    
    fig_bump_deltaT = matplotlib.figure.Figure(figsize = [10, 8])
    axis_bump_deltaT = fig_bump_deltaT.add_subplot(1, 1, 1)
    
    fig_bump_deltaT_mean = matplotlib.figure.Figure(figsize = [10, 8])
    axis_bump_deltaT_mean = fig_bump_deltaT_mean.add_subplot(1, 1, 1)
    
    fig_foms = matplotlib.figure.Figure(figsize = [10, 8])
    axis_foms = fig_foms.add_subplot(1, 1, 1)
    
    fig_fom1 = matplotlib.figure.Figure(figsize = [10, 8])
    axis_fom1 = fig_fom1.add_subplot(1, 1, 1)
    
    fig_fom_signi = matplotlib.figure.Figure(figsize = [10, 8])
    axis_fom_signi = fig_fom_signi.add_subplot(1, 1, 1)
    
    fig_correlation = matplotlib.figure.Figure(figsize = [10, 8])
    axis_correlation = fig_correlation.add_subplot(1, 1, 1)
    
    
    h1_temp = ROOT.TH1F("h1_temp", "h1_temp", 200, -10.0, 0.0)
    
    
    title_latex = args.title
    
    title_latex = title_latex.replace("_", "\_")
    
    
    d_Lyon_deltaT = {}
    
    if (args.lyonDTfile is not None) :
        
        arr_Lyon_deltaT = numpy.loadtxt(args.lyonDTfile, delimiter = ",", dtype = str)
        
        for ele1, ele2 in arr_Lyon_deltaT :
            
            ele1 = ele1.strip()
            ele2 = ele2.strip()
            #print(ele1, ele2)
            d_Lyon_deltaT[ele1] = float(ele2)
    
    
    cfoam_count = -1
    
    l_fom_label = []
    d_fom_label = {}
    
    d_fom = {}
    
    for iCfoam, cfoam_label in enumerate(l_cfoam_label_sorted) :
        
        if (args.side == constants.side_top_str) :
            
            if (not (iCfoam+1)%2) : continue
        
        elif (args.side == constants.side_bottom_str) :
            
            if ((iCfoam+1)%2) : continue
        
        cfoam_count += 1
        
        header = "{s} {cf} {s}".format(s = "*"*10, cf = cfoam_label)
        print()
        print("*"*len(header))
        print(header)
        print("*"*len(header))
        
        cfoam_label_safe = cfoam_label.replace("/", "_")
        
        fig_profile = matplotlib.figure.Figure(figsize = [10, 8])
        axis_profile = fig_profile.add_subplot(1, 1, 1)
        
        #f ("R7/" not in cfoam_label) : continue
        #if (cfoam_label != "R7/CF3") : continue
        
        maxTemp_global = -999999.0
        maxTemp_global_smooth = -999999.0
        
        minTemp_global = 999999.0
        minTemp_global_smooth = 999999.0
        
        d_arr_prof_yy = {}
        d_arr_prof_yy_smooth = {}
        
        for iProf, prof_label in enumerate(d_profileData[cfoam_label]) :
            
            arr_prof_yy = numpy.array(d_profileData[cfoam_label][prof_label]["yy"], dtype = float)
            
            if (not len(arr_prof_yy) or cfoam_label in args.skipCfoams) :
            #if (len(arr_prof_yy) < 150) :
                
                #arr_prof_yy = numpy.zeros(1)
                arr_prof_yy = numpy.array([numpy.nan])
            
            arr_prof_yy_smooth = numpy.zeros(len(arr_prof_yy))
            
            window_length = 51
            #window_length = min(window_length, len(arr_prof_yy))
            
            if (len(arr_prof_yy) >= window_length) :
                
                arr_prof_yy_smooth = scipy.signal.savgol_filter(
                    arr_prof_yy,
                    window_length = window_length,
                    polyorder = 2,
                    deriv = 0, # Default 0
                    delta = 1.0, # Default 1.0
                    mode = "interp", # Default interp
                    cval = 0.0 # Default 0.0
                )
            
            d_arr_prof_yy[prof_label] = arr_prof_yy
            d_arr_prof_yy_smooth[prof_label] = arr_prof_yy_smooth
            
            maxTemp_global = max(maxTemp_global, max(arr_prof_yy))
            maxTemp_global_smooth = max(maxTemp_global_smooth, max(arr_prof_yy_smooth))
            
            minTemp_global = min(minTemp_global, min(arr_prof_yy))
            minTemp_global_smooth = min(minTemp_global_smooth, min(arr_prof_yy_smooth))
            
            
            arr_weight = numpy.ones(len(arr_prof_yy_smooth))
            
            h1_temp.FillN(len(arr_prof_yy_smooth), arr_prof_yy_smooth, arr_weight)
        
        
        l_xtick.append(iCfoam)
        l_xtick_label.append(cfoam_label)
        
        
        nElement = min([len(ele) for ele in list(d_arr_prof_yy_smooth.values())])
        arr = numpy.array([ele[0: nElement] for ele in list(d_arr_prof_yy_smooth.values())])
        #print(arr)
        #print(arr.shape)
        arr_std = numpy.std(arr, axis = 0)
        arr_mean = numpy.mean(arr, axis = 0)
        #print(arr_std.shape)
        arr_std_mean = numpy.mean(arr_std)
        #arr_std_mean = numpy.mean(arr_std/numpy.abs(arr_mean))
        #print("arr_std_mean:", arr_std_mean)
        #print("arr_std_max:", numpy.max(arr_std))
        #exit()
        
        l_deltaT = []
        l_bump_deltaT = []
        
        for iProf, prof_label in enumerate(d_arr_prof_yy) :
            
            arr_prof_yy = d_arr_prof_yy[prof_label]
            arr_prof_yy_smooth = d_arr_prof_yy_smooth[prof_label]
            
            #yf = scipy.fft.fft(arr_prof_yy)
            #xf = scipy.fft.fftfreq(len(arr_prof_yy), 1.0)
            #xf = scipy.fft.fftfreq(len(arr_prof_yy)*1000, 1.0/1000)
            
            #matplotlib.pyplot.plot(xf, numpy.abs(yf))
            
            prom = 0.7 - (minTemp_global_smooth + 10)*0.0948
            
            peaks, d_peak_properties = scipy.signal.find_peaks(
                arr_prof_yy_smooth,
                #height = 0.2,
                #threshold = 0.2,
                #distance = 20,
                #prominence = 0.5,
                prominence = 0.4,
                #prominence = prom,
            )
            
            valleys, d_valley_properties = scipy.signal.find_peaks(
                #-1*arr_prof_yy_smooth,
                -1*arr_prof_yy_smooth,
                #height = 0.2,
                #threshold = 0.2,
                #distance = 20,
                prominence = 0.5,
                #prominence = 1.0,
                #prominence = 0.5*abs(minTemp_global_smooth),
                #prominence = prom,
            )
            
            print("Peak idx:        ", peaks)
            print("Peak val:        ", arr_prof_yy_smooth[peaks])
            print("Peak prominance: ", d_peak_properties["prominences"])
            
            print("Valley idx:        ", valleys)
            print("Valley val:        ", arr_prof_yy_smooth[valleys])
            print("Valley prominance: ", d_valley_properties["prominences"])
            
            x1 = int(len(arr_prof_yy_smooth)/5)
            x2 = len(arr_prof_yy_smooth) - x1
            print(x1, x2)
            
            peak_idx = numpy.argwhere((peaks > x1) * (peaks < x2))
            peaks = peaks[peak_idx]
            #print(peaks)
            
            valley_idx = numpy.argwhere((valleys > x1) * (valleys < x2))
            valleys = valleys[valley_idx]
            
            
            axis_profile.plot(
                list(range(len(arr_prof_yy))),
                arr_prof_yy,
                linestyle = "-",
                linewidth = 2,
                color = colors.highContrastColors_2[iProf],
                alpha = 0.25,
            )
            
            axis_profile.plot(
                list(range(len(arr_prof_yy_smooth))),
                arr_prof_yy_smooth,
                linestyle = "--",
                linewidth = 2,
                color = colors.highContrastColors_2[iProf],
            )
            
            
            if (len(peaks)) :
                
                axis_profile.plot(
                    peaks,
                    arr_prof_yy_smooth[peaks],
                    color = colors.highContrastColors_2[iProf],
                    linestyle = "none",
                    marker = "o",
                    markeredgecolor = "black",
                    markersize = 7,
                    #fillstyle = "none",
                )
                
                #arr_prof_dyy_smooth = arr_prof_yy_smooth[peaks] - minTemp_global_smooth
                arr_prof_dyy_smooth = d_peak_properties["prominences"][peak_idx]
                
                axis_bump_deltaT.plot(
                    [iCfoam] * len(peaks),
                    arr_prof_dyy_smooth,
                    color = colors.highContrastColors_2[iProf],
                    linestyle = "none",
                    marker = "o",
                    fillstyle = "none",
                )
                
                l_bump_deltaT.extend(arr_prof_dyy_smooth.tolist())
            
            else :
                
                axis_bump_deltaT.plot(
                    [iCfoam],
                    [0],
                    color = colors.highContrastColors_2[iProf],
                    linestyle = "none",
                    marker = "o",
                    fillstyle = "none",
                )
            
            
            #if (len(valleys)) :
            #    
            #    axis_profile.plot(
            #        valleys,
            #        arr_prof_yy_smooth[valleys],
            #        color = colors.highContrastColors_2[iProf],
            #        linestyle = "none",
            #        marker = "o",
            #        markeredgecolor = "black",
            #        markersize = 7,
            #        #fillstyle = "none",
            #    )
            #    
            #    #arr_prof_dyy_smooth = arr_prof_yy_smooth[valleys] - minTemp_global_smooth
            #    arr_prof_dyy_smooth = d_valley_properties["prominences"][valley_idx]
            #    
            #    axis_bump_deltaT.plot(
            #        [iCfoam] * len(valleys),
            #        arr_prof_dyy_smooth,
            #        color = colors.highContrastColors_2[iProf],
            #        linestyle = "none",
            #        marker = "o",
            #        fillstyle = "none",
            #    )
            #    
            #    l_bump_deltaT.extend(arr_prof_dyy_smooth.tolist())
            #
            #else :
            #    
            #    axis_bump_deltaT.plot(
            #        [iCfoam],
            #        [0],
            #        color = colors.highContrastColors_2[iProf],
            #        linestyle = "none",
            #        marker = "o",
            #        fillstyle = "none",
            #    )
            
            
            
            #arr_profSegment_yy = numpy.array_split(arr_prof_yy, indices_or_sections = nSegment)
            arr_profSegment_yy = numpy.array_split(arr_prof_yy_smooth, indices_or_sections = nSegment)
            
            for iSeg, seg_yy in enumerate(arr_profSegment_yy) :
                
                if (not len(seg_yy)) :
                    
                    continue
                
                #if (iSeg in [0, len(arr_profSegment_yy)-1]) : continue
                if (iSeg in args.nSegExc[1:]) : continue
                
                minTemp = min(seg_yy)
                deltaT = minTemp - minTemp_global_smooth
                
                l_deltaT.append(deltaT)
                
                print("{label}, segment {segment}, min temp. {minTemp:+0.2f}, deltaT {deltaT:+0.2f}, ".format(
                    label = prof_label,
                    segment = iSeg,
                    minTemp = minTemp,
                    deltaT = deltaT,
                ))
                
                #segment_label = "segment%d" %(iSeg+1)
                #
                #if (segment_label not in d_plot_xy) :
                #    
                #    d_plot_xy[segment_label] = []
                
                plot_x = iCfoam*10 + iSeg
                plot_y = deltaT
                
                #d_plot_xy[segment_label]
                
                #matplotlib.pyplot.plot(
                #    plot_x, plot_y,
                #    c = colors.highContrastColors_2[iProf],
                #    marker = l_marker[iSeg],
                #    fillstyle = "none",
                #    markersize = 5,
                #)
        
        #matplotlib.pyplot.show()
        
        
        l_deltaT = [ele for ele in l_deltaT if (ele > 0)]
        
        if (not len(l_deltaT)) :
            
            #l_deltaT = [-0.1]
            l_deltaT = [numpy.nan]
        
        #print(l_deltaT); exit()
        #plot_x = iCfoam
        deltaT = numpy.mean(l_deltaT)
        #deltaT = numpy.mean([ele for ele in l_deltaT if ele > 0])
        #deltaT = max(l_deltaT)
        deltaT_err_pos = max(l_deltaT) - deltaT
        deltaT_err_neg = deltaT - min(l_deltaT)
        
        print(deltaT, deltaT_err_pos, deltaT_err_neg)
        
        axis_deltaT.errorbar(
            [iCfoam],
            [deltaT],
            yerr = [[deltaT_err_neg], [deltaT_err_pos]],
            c = colors.highContrastColors_2[0],
            marker = l_marker[0],
            fillstyle = "none",
            markersize = 5,
        )
        
        bump_deltaT_max = max(l_bump_deltaT) if len(l_bump_deltaT) else 0
        bump_deltaT_sum = numpy.sum(l_bump_deltaT) if len(l_bump_deltaT) else 0
        bump_deltaT_mean = numpy.mean(l_bump_deltaT) if len(l_bump_deltaT) else 0
        
        axis_bump_deltaT_mean.plot(
            [iCfoam],
            [bump_deltaT_mean*len(l_bump_deltaT)],
            color = colors.highContrastColors_2[0],
            marker = l_marker[0],
            fillstyle = "none",
            markersize = 5,
        )
        
        axis_profile_stdDev_mean.plot(
            [iCfoam],
            [arr_std_mean],
            #[arr_std_mean/abs(minTemp_global_smooth)*10.0],
            color = colors.highContrastColors_2[0],
            marker = l_marker[0],
            fillstyle = "none",
            markersize = 5,
        )
        
        
        norm = 1.0 / (0.0-minTemp_global_smooth)
        
        # FOMs
        fom_label_idx = -1
        
        fom_label_idx += 1
        #fom_label = "avg($\\Delta T_\\text{min}$)"
        fom_label = "$\\text{FOM1} = \\max(\\Delta T_\\text{min}) - \\min(\\Delta T_\\text{min})$"
        d_fom_label[fom_label] = fom_label_idx
        if (not cfoam_count) : l_fom_label.append(fom_label)
        if (fom_label not in d_fom) : d_fom[fom_label] = {"x": [], "y": []}
        d_fom[fom_label]["x"].append(iCfoam)
        #d_fom[fom_label]["y"].append(deltaT)
        #d_fom[fom_label]["y"].append(max(l_deltaT)-min(l_deltaT))
        d_fom[fom_label]["y"].append((max(l_deltaT)-min(l_deltaT)) * norm * 5)
        if (cfoam_label in args.skipCfoams) : d_fom[fom_label]["y"][-1] = numpy.nan
        #axis_foms.errorbar(
        #    [iCfoam],
        #    [deltaT],
        #    yerr = [[deltaT_err_neg], [deltaT_err_pos]],
        #    c = colors.highContrastColors_2[0],
        #    marker = l_marker[0],
        #    #fillstyle = "none",
        #    markersize = 5,
        #    linestyle = "none",
        #    label = (fom_label if (not cfoam_count) else None),
        #)
        
        fom_label_idx += 1
        fom_label = "$\\text{FOM2} = \\sum(\\Delta T_\\text{bump})$"
        d_fom_label[fom_label] = fom_label_idx
        if (not cfoam_count) : l_fom_label.append(fom_label)
        if (fom_label not in d_fom) : d_fom[fom_label] = {"x": [], "y": []}
        d_fom[fom_label]["x"].append(iCfoam)
        d_fom[fom_label]["y"].append(bump_deltaT_sum/len(d_arr_prof_yy))
        if (cfoam_label in args.skipCfoams) : d_fom[fom_label]["y"][-1] = numpy.nan
        
        #axis_foms.plot(
        #    [iCfoam],
        #    [bump_deltaT_sum/len(d_arr_prof_yy)],
        #    #[min(3.0, bump_deltaT_sum)],
        #    #[bump_deltaT_mean],
        #    color = colors.highContrastColors_2[1],
        #    marker = l_marker[0],
        #    #fillstyle = "none",
        #    markersize = 5,
        #    linestyle = "none",
        #    label = (fom_label if (not cfoam_count) else None),
        #)
        
        fom_label_idx += 1
        fom_label = "$\\text{FOM3} = \\langle\\sigma_T\\rangle$ [$\\times 50$]"
        d_fom_label[fom_label] = fom_label_idx
        if (not cfoam_count) : l_fom_label.append(fom_label)
        if (fom_label not in d_fom) : d_fom[fom_label] = {"x": [], "y": []}
        d_fom[fom_label]["x"].append(iCfoam)
        #d_fom[fom_label]["y"].append(arr_std_mean*10)
        d_fom[fom_label]["y"].append(arr_std_mean*50 * norm)
        if (cfoam_label in args.skipCfoams) : d_fom[fom_label]["y"][-1] = numpy.nan
        #axis_foms.plot(
        #    [iCfoam],
        #    #[arr_std_mean],
        #    [arr_std_mean*20],
        #    #[arr_std_mean/abs(minTemp_global_smooth)*10.0],
        #    color = colors.highContrastColors_2[2],
        #    marker = l_marker[0],
        #    #fillstyle = "none",
        #    markersize = 5,
        #    linestyle = "none",
        #    label = (fom_label if (not cfoam_count) else None),
        #)
        
        if (d_Lyon_deltaT) :
            
            fom_label_idx += 1
            fom_label = "Lyon $\\Delta T$ [$\\times 0.1$]"
            d_fom_label[fom_label] = fom_label_idx
            if (not cfoam_count) : l_fom_label.append(fom_label)
            if (fom_label not in d_fom) : d_fom[fom_label] = {"x": [], "y": []}
            d_fom[fom_label]["x"].append(iCfoam)
            d_fom[fom_label]["y"].append(d_Lyon_deltaT[cfoam_label_safe]/10.0)
            if (cfoam_label in args.skipCfoams) : d_fom[fom_label]["y"][-1] = numpy.nan
            #axis_foms.plot(
            #    [iCfoam],
            #    [d_Lyon_deltaT[cfoam_label_safe]/10.0],
            #    color = colors.highContrastColors_2[3],
            #    marker = l_marker[1],
            #    #fillstyle = "none",
            #    markersize = 5,
            #    linestyle = "none",
            #    label = (fom_label if (not cfoam_count) else None),
            #)
        
        
        #fom1 = deltaT + bump_deltaT_max
        #fom1 = (deltaT + bump_deltaT_max) / (1.0+bool(len(l_bump_deltaT)))
        #fom1 = deltaT + bump_deltaT_mean
        #fom1 = deltaT + bump_deltaT_sum
        #fom1 = deltaT + bump_deltaT_mean + arr_std_mean
        fom1 = (deltaT**2 + bump_deltaT_mean**2 + arr_std_mean**2)**0.5
        #fom1 = arr_std_mean
        
        
        axis_fom1.plot(
            [iCfoam],
            [fom1],
            color = colors.highContrastColors_2[0],
            marker = l_marker[0],
            fillstyle = "none",
            markersize = 5,
        )
        
        
        # Correlation plot
        #axis_correlation.plot(
        #    [d_Lyon_deltaT[cfoam_label_safe]],
        #    [deltaT_err_pos],
        #    #[arr_std_mean/abs(minTemp_global_smooth)*10.0],
        #    color = colors.highContrastColors_2[0],
        #    marker = l_marker[0],
        #    fillstyle = "none",
        #    markersize = 5,
        #)
        #
        #axis_correlation.plot(
        #    [d_Lyon_deltaT[cfoam_label_safe]],
        #    [arr_std_mean*10],
        #    #[arr_std_mean/abs(minTemp_global_smooth)*10.0],
        #    color = colors.highContrastColors_2[1],
        #    marker = l_marker[0],
        #    fillstyle = "none",
        #    markersize = 5,
        #)
        
        
        ylim1 = numpy.floor(minTemp_global-0.5)
        ylim2 = ylim1+5
        axis_profile.set_ylim(ylim1, ylim2)
        axis_profile.grid(visible = True, which = "major", axis = "y", linestyle = "--")
        axis_profile.set_title("%s\n%s" %(title_latex, cfoam_label))
        axis_profile.figure.tight_layout()
        axis_profile.figure.savefig("%s/%s_smooth-profiles.pdf" %(outdir, cfoam_label_safe))
    
    
    for iFom, fom_label in enumerate(d_fom) :
        
        axis_foms.plot(
            d_fom[fom_label]["x"],
            d_fom[fom_label]["y"],
            color = colors.highContrastColors_2[iFom],
            marker = l_marker[iFom],
            #fillstyle = "none",
            markersize = 5,
            #linestyle = "none",
            linestyle = "-",
            #label = (fom_label if (not cfoam_count) else None),
            label = fom_label,
        )
    
    
    arr_fom_signi = numpy.zeros(len(d_fom[list(d_fom.keys())[0]]["x"]))
    arr_fom_signi_lyon = None
    
    fom_count = 0
    
    #for iFom, fom_label in enumerate(list(d_fom.keys())[::-1]) :
    for iFom, fom_label in enumerate(d_fom) :
        
        fom_count += 1
        
        arr = numpy.array(d_fom[fom_label]["y"])
        
        fom_avg = numpy.nanmean(arr)
        fom_min = numpy.nanmin(arr)
        fom_std = numpy.nanstd(arr)
        
        fom_signi = (arr-fom_min) / fom_std
        
        print(fom_label, fom_signi)
        
        handles_, labels_ = axis_foms.get_legend_handles_labels()
        handle = handles_[labels_.index(fom_label)]
        
        handle_label = handle.get_label()
        
        if ("Lyon" not in handle_label) :
            
            print("Adding to FOM significance.")
            arr_fom_signi = arr_fom_signi + fom_signi**2
            #arr_fom_signi = numpy.maximum(arr_fom_signi, fom_signi)
            #print(fom_label, fom_signi)
        
        #print(type(handle))
        #print(handle.__dict__)
        
        if (isinstance(handle, matplotlib.container.ErrorbarContainer)) :
            
            handle = handle.lines[0]
        
        #elif (isinstance(handle, matplotlib.container.ErrorbarContainer)) :
        
        #print(d_fom[fom_label]["x"])
        #print(fom_signi)
        
        if ("Lyon" in handle_label) :
            
            fom_count -= 1
            
            arr_fom_signi_lyon = fom_signi
            
            axis_fom_signi.plot(
                d_fom[fom_label]["x"],
                fom_signi,
                #color = colors.highContrastColors_2[iFom],
                color = handle.get_color(),
                #marker = l_marker[0],
                marker = handle.get_marker(),
                #fillstyle = "none",
                markersize = 5,
                #linestyle = "none",
                linestyle = "-",
                #label = handle_label,
                label = "$\\hat{z}(\\text{Lyon }\\Delta T)$",
            )
        
        #axis_fom_signi.plot(
        #    d_fom[fom_label]["x"],
        #    fom_signi,
        #    #color = colors.highContrastColors_2[iFom],
        #    color = handle.get_color(),
        #    #marker = l_marker[0],
        #    marker = handle.get_marker(),
        #    #fillstyle = "none",
        #    markersize = 5,
        #    #linestyle = "none",
        #    linestyle = "-",
        #    label = handle_label,
        #    #label = "$\\hat{z}(\\text{%s})$" %(handle_label),
        #)
        
    
    arr_fom_signi = arr_fom_signi**0.5 / fom_count
    
    #print("arr_fom_signi:", arr_fom_signi)
    
    axis_fom_signi.plot(
        d_fom[list(d_fom.keys())[0]]["x"],
        arr_fom_signi,
        color = colors.highContrastColors_2[len(d_fom)],
        marker = l_marker[len(d_fom)],
        #fillstyle = "none",
        markersize = 5,
        #linestyle = "none",
        linestyle = "-",
        label = "$\\hat{z}(\\text{all FOMs})$",
        #label = "all-DESY-FOMs",
    )
    
    if (args.lyonDTfile is not None) :
        
        axis_correlation.plot(
            arr_fom_signi_lyon,
            arr_fom_signi,
            color = colors.highContrastColors_2[0],
            marker = l_marker[0],
            linestyle = "none",
            #fillstyle = "none",
            markersize = 5,
        )
        
        
        fitFunc = lambda x, p0, p1: p0 + p1*x
        fitParVals, fitParCovs = scipy.optimize.curve_fit(f = fitFunc, xdata = arr_fom_signi_lyon, ydata = arr_fom_signi, check_finite = False)
        fitParErrs = numpy.sqrt(numpy.diag(fitParCovs))
        fitLabel = "y = (%0.2f±%0.2f) + (%0.2f±%0.2f)x" %(fitParVals[0], fitParErrs[0], fitParVals[1], fitParErrs[1])
        print(fitLabel)
    
    
    axis_deltaT.set_xlim(-3, len(l_cfoam_label_sorted)+1)
    axis_deltaT.set_ylim(0, 3.0)
    axis_deltaT.set_xticks(l_xtick)#, l_xtick_label, fontsize = "xx-small", rotation = 45)
    axis_deltaT.set_xticklabels(l_xtick_label, fontsize = "xx-small", rotation = 45)
    axis_deltaT.grid(visible = True, which = "major", axis = "both", linestyle = "--")
    axis_deltaT.set_title(title_latex, fontsize = "x-large")
    axis_deltaT.figure.tight_layout()
    axis_deltaT.figure.savefig("%s/profile_deltaT.pdf" %(outdir))
    
    
    axis_bump_deltaT.set_xlim(-3, len(l_cfoam_label_sorted)+1)
    axis_bump_deltaT.set_ylim(0, 3.0)
    axis_bump_deltaT.set_xticks(l_xtick)#, l_xtick_label, fontsize = "xx-small", rotation = 45)
    axis_bump_deltaT.set_xticklabels(l_xtick_label, fontsize = "xx-small", rotation = 45)
    axis_bump_deltaT.grid(visible = True, which = "major", axis = "both", linestyle = "--")
    axis_bump_deltaT.set_title(title_latex, fontsize = "x-large")
    axis_bump_deltaT.figure.tight_layout()
    axis_bump_deltaT.figure.savefig("%s/bump_deltaT.pdf" %(outdir))
    axis_bump_deltaT.set_ylim(0, 4.0)
    
    
    axis_bump_deltaT_mean.set_xlim(-3, len(l_cfoam_label_sorted)+1)
    axis_bump_deltaT_mean.set_ylim(0, 5.0)
    axis_bump_deltaT_mean.set_xticks(l_xtick)#, l_xtick_label, fontsize = "xx-small", rotation = 45)
    axis_bump_deltaT_mean.set_xticklabels(l_xtick_label, fontsize = "xx-small", rotation = 45)
    axis_bump_deltaT_mean.grid(visible = True, which = "major", axis = "both", linestyle = "--")
    axis_bump_deltaT_mean.set_title(title_latex, fontsize = "x-large")
    axis_bump_deltaT_mean.figure.tight_layout()
    axis_bump_deltaT_mean.figure.savefig("%s/bump_deltaT_mean.pdf" %(outdir))
    
    
    axis_profile_stdDev_mean.set_xlim(-3, len(l_cfoam_label_sorted)+1)
    axis_profile_stdDev_mean.set_ylim(0, 0.5)
    axis_profile_stdDev_mean.set_xticks(l_xtick)#, l_xtick_label, fontsize = "xx-small", rotation = 45)
    axis_profile_stdDev_mean.set_xticklabels(l_xtick_label, fontsize = "xx-small", rotation = 45)
    axis_profile_stdDev_mean.grid(visible = True, which = "major", axis = "both", linestyle = "--")
    axis_profile_stdDev_mean.set_title(title_latex, fontsize = "x-large")
    axis_profile_stdDev_mean.figure.tight_layout()
    axis_profile_stdDev_mean.figure.savefig("%s/profile_stdDev_mean.pdf" %(outdir))
    
    
    axis_foms.set_xlim(-3, len(l_cfoam_label_sorted)+1)
    axis_foms.set_ylim(0, 3.0)
    axis_foms.set_ylabel("a.u.", fontsize = 20)
    axis_foms.set_xticks(l_xtick)#, l_xtick_label, fontsize = "xx-small", rotation = 45)
    axis_foms.set_xticklabels(l_xtick_label, fontsize = "medium", rotation = 90, weight = "bold")
    axis_foms.tick_params(axis = "y", labelsize = "x-large")
    axis_foms.grid(visible = True, which = "major", axis = "both", linestyle = "--")
    handles_, labels_ = axis_foms.get_legend_handles_labels()
    handles = [handles_[labels_.index(ele)] for ele in l_fom_label]
    axis_foms.legend(handles, l_fom_label, fontsize = "x-large")
    axis_foms.set_title(title_latex, fontsize = "x-large")
    axis_foms.figure.tight_layout()
    axis_foms.figure.savefig("%s/foms.pdf" %(outdir))
    
    
    axis_fom_signi.set_xlim(-3, len(l_cfoam_label_sorted)+1)
    axis_fom_signi.set_ylim(0, 7.0)
    axis_fom_signi.set_ylabel("$\\hat{z}$", fontsize = 20)
    axis_fom_signi.set_xticks(l_xtick)#, l_xtick_label, fontsize = "xx-small", rotation = 45)
    axis_fom_signi.set_xticklabels(l_xtick_label, fontsize = "medium", rotation = 90, weight = "bold")
    axis_fom_signi.tick_params(axis = "y", labelsize = "x-large")
    axis_fom_signi.grid(visible = True, which = "major", axis = "both", linestyle = "--")
    #handles_, labels_ = axis_fom_signi.get_legend_handles_labels()
    #handles = [handles_[labels_.index(ele)] for ele in l_fom_label]
    #axis_fom_signi.legend(handles, l_fom_label, fontsize = "x-large")
    axis_fom_signi.legend(fontsize = "x-large")
    axis_fom_signi.set_title(title_latex, fontsize = "x-large")
    axis_fom_signi.figure.tight_layout()
    axis_fom_signi.figure.savefig("%s/fom_signi.pdf" %(outdir))
    
    
    axis_fom1.set_xlim(-3, len(l_cfoam_label_sorted)+1)
    axis_fom1.set_ylim(0, 3.0)
    axis_fom1.set_xticks(l_xtick)#, l_xtick_label, fontsize = "xx-small", rotation = 45)
    axis_fom1.set_xticklabels(l_xtick_label, fontsize = "xx-small", rotation = 45)
    axis_fom1.grid(visible = True, which = "major", axis = "both", linestyle = "--")
    axis_fom1.set_title(title_latex, fontsize = "x-large")
    axis_fom1.figure.tight_layout()
    axis_fom1.figure.savefig("%s/fom1.pdf" %(outdir))
    
    
    axis_correlation.set_xlim(0, 5.0)
    axis_correlation.set_ylim(0, 5.0)
    #axis_correlation.set_xticks(l_xtick)#, l_xtick_label, fontsize = "xx-small", rotation = 45)
    #axis_correlation.set_xticklabels(l_xtick_label, fontsize = "xx-small", rotation = 45)
    axis_correlation.grid(visible = True, which = "major", axis = "both", linestyle = "--")
    axis_correlation.set_title(title_latex, fontsize = "x-large")
    axis_correlation.figure.tight_layout()
    axis_correlation.figure.savefig("%s/correlation.pdf" %(outdir))
    
    
    
    
    #canvas = ROOT.TCanvas("canvas", "canvas", 600, 600)
    #canvas.cd()
    #h1_temp.Draw("hist")
    #canvas.SaveAs("tmp/hist_profile.pdf")


if (__name__ == "__main__") :
    
    main()
