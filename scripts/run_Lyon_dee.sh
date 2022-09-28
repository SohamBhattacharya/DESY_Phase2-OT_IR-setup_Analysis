#!/usr/bin/env python

import os



def main() :
    
    l_config = [
        #"Lyon_dee_no-connector_side_2Sinserts_lamp_off_2021-10-13",
        "Lyon_dee_disk2disk-connector_side_2Sinserts_lamp_off_2021-12-02",
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
