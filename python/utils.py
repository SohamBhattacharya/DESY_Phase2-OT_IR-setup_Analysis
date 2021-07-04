def motor_stepX_to_mm(val, inv = False) :
    
    f = 1920.0/34952
    #f = 1920.0/35157
    
    if (inv) :
        
        return val / f
    
    else :
        
        return val * f


def motor_stepY_to_mm(val, inv = False) :
    
    f = 895.0/716059
    #f = 895.0/713540
    
    if (inv) :
        
        return val / f
    
    else :
        
        return val * f


def mm_to_pix(val, inv = False) :
    
    f = 319/55.26
    #f = 310/55.26
    
    if (inv) :
        
        return val / f
    
    else :
        
        return val * f


def motor_stepX_to_pix(val, inv = False) :
    
    if (inv) :
        
        return motor_stepX_to_mm(mm_to_pix(val, inv), inv)
    
    else :
        
        return mm_to_pix(motor_stepX_to_mm(val, inv), inv)


def motor_stepY_to_pix(val, inv = False) :
    
    if (inv) :
        
        return motor_stepY_to_mm(mm_to_pix(val, inv), inv)
    
    else :
        
        return mm_to_pix(motor_stepY_to_mm(val, inv), inv)


def clean_string(s, l_clean = [" "]) :
    
    for cl in l_clean :
        
        while(cl in s) :
            
            s = s.replace(cl, "")
    
    
    return s
