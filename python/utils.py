import copy
import re


def clean_string(s, l_clean = [" "]) :
    
    for cl in l_clean :
        
        while(cl in s) :
            
            s = s.replace(cl, "")
    
    
    return s


def reset_artist(artist) :
    
    artist.axes = None
    artist.figure = None


def copy_and_reset_artist(artist) :
    
    artist_copy = reset_artist(copy.copy(artist))
    
    return artist_copy


def naturalsort(l) :
    
    return sorted(l, key = lambda s: [int(c) if c.isdigit() else c for c in re.split("(\d+)", s)])


def setAxisBoxColor(ax, color) :
    
    ax.spines["bottom"].set_color(color)
    ax.spines["top"].set_color(color) 
    ax.spines["right"].set_color(color)
    ax.spines["left"].set_color(color)
