import argparse
import numpy
import os

import utils


def main() :
    
    # Argument parser
    parser = argparse.ArgumentParser(formatter_class = argparse.ArgumentDefaultsHelpFormatter)
    
    parser.add_argument(
        "--lampoffDir",
        help = "Directory with lamp off results",
        type = str,
        required = True,
    )
    
    parser.add_argument(
        "--lamponDir",
        help = "Directory with lamp on results",
        type = str,
        required = False,
        default = None,
    )
    
    parser.add_argument(
        "--fileNameSuffix",
        help = "File name suffix (including the leading separator such as underscore)",
        type = str,
        required = False,
        default = "",
    )
    
    parser.add_argument(
        "--outDir",
        help = "Output directory",
        type = str,
        required = True,
    )
    
    parser.add_argument(
        "--templateDir",
        help = "Template directory (there needs to be a file <templateDir>.tex in here)",
        type = str,
        required = False,
        default = "cfoam_slides_template",
    )
    
    parser.add_argument(
        "--title",
        help = "Slide title",
        type = str,
        required = False,
        default = "Carbon foams",
    )
    
    parser.add_argument(
        "--loadDT",
        help = "Load DeltaT csv.",
        type = str,
        required = False,
    )
    
    parser.add_argument(
        "--overwrite",
        help = "Overwrite output directory",
        default = False,
        action = "store_true",
    )
    
    
    args = parser.parse_args()
    d_args = vars(args)
    
    
    if (os.path.exists(args.outDir) and not args.overwrite) :
        
        print("Output directory already exists: %s" %(args.outDir))
        print("Exiting...")
        exit(1)
    
    
    d_deltaT = {}
    
    if (args.loadDT) :
        
        arr_deltaT = numpy.loadtxt(args.loadDT, delimiter = ",", dtype = str)
        
        for ele in arr_deltaT :
            
            name = ele[0].strip()
            dT = float(ele[1].strip())
            
            d_deltaT[name] = dT
        
        print(d_deltaT)
    
    
    l_ring = list(range(1, 16))
    l_cfoam = list(range(1, 25))
    
    
    output_tex = """"""
    
    tex_links = ""
    tex_links += "\\hyperlink{fr:stitchedimage_lampoff}{dee lamp off}\\\\ "
    if (args.lamponDir is not None) : tex_links += "\\hyperlink{fr:stitchedimage_lampon}{dee lamp on}\\\\ "
    
    for iRing, ring in enumerate(l_ring) :
        
        for iCfoam, cfoam in enumerate(l_cfoam) :
            
            cfoamName = "R%s_CF%s" %(ring, cfoam)
            cfoamName_tex = "R%s\_CF%s" %(ring, cfoam)
            
            cfoamDir_lampoff = "%s/%s" %(args.lampoffDir, cfoamName)
            cfoamDir_lampon = "%s/%s" %(args.lamponDir, cfoamName) if (args.lamponDir is not None) else ""
            
            #print(cfoamDir_lampoff)
            #print(cfoamDir_lampon)
            
            if (not os.path.exists(cfoamDir_lampoff) or (args.lamponDir is not None and not os.path.exists(cfoamDir_lampon))) :
                
                continue
            
            cfoam_lampoff = "%s/%s%s.pdf" %(cfoamDir_lampoff, cfoamName, args.fileNameSuffix)
            cfoam_lampon = "%s/%s%s.pdf" %(cfoamDir_lampon, cfoamName, args.fileNameSuffix) if (args.lamponDir is not None) else ""
            
            prof_lampoff = "%s/%s_profiles%s.pdf" %(cfoamDir_lampoff, cfoamName, args.fileNameSuffix)
            prof_lampon = "%s/%s_profiles%s.pdf" %(cfoamDir_lampon, cfoamName, args.fileNameSuffix) if (args.lamponDir is not None) else ""
            
            
            tex_slide = utils.get_cfoam_slide_template()
            
            tex_slide = tex_slide.replace("<frametitle>", cfoamName_tex)
            
            framelabel = "fr:%s" %(cfoamName)
            tex_slide = tex_slide.replace("<framelabel>", framelabel)
            
            tex_slide = tex_slide.replace("<cfoam_lampoff>", cfoam_lampoff)
            tex_slide = tex_slide.replace("<prof_lampoff>", prof_lampoff)
            
            if (args.lamponDir is not None) : 
                
                tex_slide = tex_slide.replace("<cfoam_lampon>", cfoam_lampon)
                tex_slide = tex_slide.replace("<prof_lampon>", prof_lampon)
            
            #print(tex_slide)
            
            #tex_links += "\\hyperlink{%s}{%s}\\\\ " %(framelabel, cfoamName_tex)
            tex_links += "\\hyperlink{%s}{%s}\\\\ " %(framelabel, cfoamName_tex)
            
            text_above = ""
            
            if (cfoamName in d_deltaT) :
                
                text_above = "$ \\Delta T = %0.1f^{\circ} $C" %(d_deltaT[cfoamName])
                print(text_above)
            
            tex_slide = tex_slide.replace("<text_above>", text_above)
            
            
            # Add slide
            output_tex += tex_slide
    
    
    output_tex = output_tex.replace("<framelinks>", tex_links)
    
    print(output_tex)
    
    
    templateFileName = "%s/%s.tex" %(args.templateDir, args.templateDir)
    
    outfileContent = ""
    
    with open(templateFileName, "r") as f :
        
        outfileContent = f.read()
        
        outfileContent = outfileContent.replace("<insertslides>", output_tex)
    
    
    os.system("mkdir -p %s" %(args.outDir))
    os.system("cp -a %s/* %s/" %(args.templateDir, args.outDir))
    
    outFile = "%s/%s.tex" %(args.outDir, args.outDir.split("/")[-1])
    
    stitchedDee_lampoff = "%s/stitched_dee.pdf" %(args.lampoffDir)
    stitchedDee_lampon = "%s/stitched_dee.pdf" %(args.lamponDir) if (args.lamponDir is not None) else ""
    
    outfileContent = outfileContent.replace("<title>", args.title)
    outfileContent = outfileContent.replace("<stichedimage_lampoff>", stitchedDee_lampoff)
    outfileContent = outfileContent.replace("<stichedimage_lampon>", stitchedDee_lampon)
    
    print("Writing output file: %s" %(outFile))
    
    with open(outFile, "w") as f :
        
        f.write(outfileContent)
    
    
    # Compile latex
    # Needs to be compiled twice for certain things like page numbers
    os.system("; ".join([
        "cd %s" %(args.outDir),
        "pdflatex %s" %(outFile.split("/")[-1]),
        "pdflatex %s" %(outFile.split("/")[-1]),
    ]))
    
    
    return 0


if (__name__ == "__main__") :
    
    main()
