class UnitConversion :
    
    
    def __init__(
        self,
        args,
    ) :
        
        self.stepxtomm = eval(str(args.stepxtomm))
        self.stepytomm = eval(str(args.stepytomm))
        self.mmtopix = eval(str(args.mmtopix))
    
    
    def motor_stepX_to_mm(self, val, inv = False) :
        
        f = self.stepxtomm
        #f = 1920.0/34952
        #f = 1920.0/35157
        
        if (inv) :
            
            return val / f
        
        else :
            
            return val * f
    
    
    def motor_stepY_to_mm(self, val, inv = False) :
        
        f = self.stepytomm
        #f = 895.0/716059
        #f = 895.0/713540
        
        if (inv) :
            
            return val / f
        
        else :
            
            return val * f
    
    
    def mm_to_pix(self, val, inv = False) :
        
        f = self.mmtopix
        #f = 319/55.26
        #f = 310/55.26
        
        if (inv) :
            
            return val / f
        
        else :
            
            return val * f
    
    
    def motor_stepX_to_pix(self, val, inv = False) :
        
        if (inv) :
            
            return self.motor_stepX_to_mm(self.mm_to_pix(val, inv), inv)
        
        else :
            
            return self.mm_to_pix(self.motor_stepX_to_mm(val, inv), inv)
    
    
    def motor_stepY_to_pix(self, val, inv = False) :
        
        if (inv) :
            
            return self.motor_stepY_to_mm(self.mm_to_pix(val, inv), inv)
        
        else :
            
            return self.mm_to_pix(self.motor_stepY_to_mm(val, inv), inv)
