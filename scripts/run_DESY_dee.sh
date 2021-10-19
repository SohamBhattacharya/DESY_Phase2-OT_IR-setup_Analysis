#!/usr/bin/env python

import os



def main() :
    
    l_config = [
        "DESY_dee_bottom_side_2Sinserts_lamp_off_2021-07-30",
        "DESY_dee_top_side_2Sinserts_lamp_off_2021-07-08",
        
        #"DESY_dee_bottom_side_cfoams_lamp_off_2021-06-16",
        #"DESY_dee_bottom_side_cfoams_lamp_on_2021-06-16",
        #"DESY_dee_top_side_cfoams_lamp_off_2021-06-21",
        #"DESY_dee_top_side_cfoams_lamp_on_2021-06-21",
    ]
    
    
    for cfg in l_config :
        
        cmd = (
            "python python/stitch_images.py "
            "--loadSave configs/{cfg}.yml "
            "--saveFigsTo plots/{cfg} "
        ).format(
            cfg = cfg
        )
        
        print(cmd)
        
        os.system(cmd)
    
    
    return 0


if (__name__ == "__main__") :
    
    main()
