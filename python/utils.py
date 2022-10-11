import copy
import pandas
import re
import yaml


def get_cfoam_slide_template() :
    
    cfoam_slide_template = r"""
        \begin{frame}
            \frametitle{<frametitle>}
            
            \vspace{-10pt}
            
            <text_above>
            
            \begin{minipage}[t]{0.075\textwidth}
                \begin{adjustbox}{valign=t, max width=\columnwidth, totalheight=\textheight-2\baselineskip-2\baselineskip, keepaspectratio}
                \begin{tabular}{l}
                    <framelinks>
                \end{tabular}%
                \end{adjustbox}%
            \end{minipage}%
            %
            \begin{minipage}[t]{0.475\textwidth}
                \centering
                
                \fcolorbox{red}{yellow}{Lamp off}
                
                \begin{figure}
                    \centering
                    \includegraphics[width=\columnwidth]{<cfoam_lampoff>} \\
                    \includegraphics[width=0.8\columnwidth]{<prof_lampoff>}
                \end{figure}
                
            \end{minipage}%
            %
            \begin{minipage}[t]{0.475\textwidth}
                \centering
                
                \fcolorbox{red}{yellow}{Lamp on}
                
                \begin{figure}
                    \centering
                    \includegraphics[width=\columnwidth]{<cfoam_lampon>} \\
                    \includegraphics[width=0.8\columnwidth]{<prof_lampon>}
                \end{figure}
                
            \end{minipage}
            
            \label{<framelabel>}
        \end{frame}
        
        
    """
    
    return cfoam_slide_template


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


def load_yaml(fileName) :
    
    with open(fileName, "r") as fopen :
        
        return yaml.load(fopen.read(), Loader = yaml.FullLoader)


def load_xls(fileName) :
    
    xls = pandas.ExcelFile(fileName)
    dframe = xls.parse(0)
    
    # Clean the headers
    dframe.rename(columns = lambda x: x.strip(), inplace = True)
    
    # Skip empty lines
    dframe.dropna(how = "all", inplace = True)
    
    return dframe


def getCoolingCircuits(fileName) :
    
    d_coolCircData = load_yaml(fileName)
    
    pattern_str = "R{ring}/2S{module}_ins{insert}"
    pattern_str_regex = "R(\d+)/2S(\d+)_ins(\d+)"
    
    d_coolCirc = {}
    
    for circuit in d_coolCircData.keys() :
        
        l_insertLabel = d_coolCircData[circuit]["inserts"]
        
        #print(circuit)
        #print(l_insertLabel)
        
        d_coolCirc[circuit] = l_insertLabel
        
        if ("reflect" in d_coolCircData[circuit]) :
            
            l_insertLabel_reflect = []
            circuit_reflect = d_coolCircData[circuit]["reflect"]["name"]
            d_reflect_transformation = d_coolCircData[circuit]["reflect"]["transformation"]
            
            for insertLabel in l_insertLabel :
                
                #ring = insertLabel.split("/")[0]
                #
                #module = insertLabel.split("/")[1]
                #
                #insert = module.split("_")[1]
                #insert = insert.split("ins")[1]
                #
                #module = module.split("_")[0]
                #module = module.split("R")[0]
                
                ring, module, insert = re.findall(pattern_str_regex, insertLabel)[0]
                
                d_format = {
                    "ring": module,
                    "module": module,
                    "insert": insert,
                }
                
                #print(d_reflect_transformation)
                
                insertLabel_reflect = pattern_str.format(
                    ring = ring,
                    module = eval(d_reflect_transformation["module"][ring].format(**d_format)),
                    insert = eval(d_reflect_transformation["insert"][insert].format(**d_format))
                )
                
                l_insertLabel_reflect.append(insertLabel_reflect)
                
                #print(insertLabel, ring, module, insert, ll)
                #print(insertLabel, ring, module, insert)
                #print(insertLabel_reflect)
            
            d_coolCirc[circuit_reflect] = l_insertLabel_reflect
            
            #print(circuit_reflect)
            #print(l_insertLabel_reflect)
    
    return d_coolCirc


def clip_and_plot_outliers_y(
    ax,
    xx, yy,
    yMin, yMax,
    annotate = True,
    d_plotOpt = {
        "color": "black",
        "linestyle": "",
        "fillstyle": "full",
        "markersize": 7,
        "clip_on": False
    }
) :
    
    for xval, yval in zip(xx, yy) :
        
        if (yval > yMax) :
            
            ax.plot(xval, yMax, marker = "^", **d_plotOpt)
            
            if (annotate) :
                
                ax.annotate(
                    f"$\\mathbf{{{yval:0.2f}}}$",
                    xy = (xval, yMax),
                    xycoords = "data",
                    xytext = (0, -5),
                    textcoords = "offset points",
                    rotation = 90,
                    horizontalalignment = "center",
                    verticalalignment = "top",
                    fontsize = "large",
                    weight = "bold",
                    clip_on = False,
                )
        
        elif (yval < yMin) :
            
            ax.plot(xval, yMin, marker = "v", **d_plotOpt)
            
            if (annotate) :
                
                ax.annotate(
                    f"$\\mathbf{{{yval:0.2f}}}$",
                    xy = (xval, yMin),
                    xycoords = "data",
                    xytext = (0, -5),
                    textcoords = "offset points",
                    rotation = 90,
                    horizontalalignment = "center",
                    verticalalignment = "bottom",
                    fontsize = "large",
                    weight = "bold",
                    clip_on = False,
                )


if (__name__ == "__main__") :
    
    pass
