zorder_deeImage = 0
zorder_deeImage_focus = 1
zorder_geometryMesh = 20
zorder_geometryText = 30


odd_str = "odd"
even_str = "even"


side_top_str = "top"
side_bottom_str = "bottom"


module_PS_str = "PS"
module_2S_str = "2S"


save_extension = ".sav"


d_moduleDetails = {
    module_PS_str: {
        odd_str: {
            "ring_min": 1,
            "ring_max": 9,
        },
        
        even_str: {
            "ring_min": 2,
            "ring_max": 10,
        },
    },
    
    module_2S_str: {
        odd_str: {
            "ring_min": 11,
            "ring_max": 15,
            
        },
        
        even_str: {
            "ring_min": 12,
            "ring_max": 16,
        },
    },
}


d_side_color = {
    side_top_str: (1, 0, 1, 1),
    side_bottom_str: (0, 1, 1, 1),
}
