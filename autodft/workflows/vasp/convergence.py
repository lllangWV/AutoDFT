import os

def check_convergence(dir, ediff, ediffg, convergence_method = None):
    oszicar=os.path.join(dir,'OSZICAR')

    if os.path.exists(oszicar):
        "aborting loop because EDIFF is reached"
        
        with open(oszicar) as f:
            lines = f.readlines()
            
            de = 10
            rms=10
            for line in lines:
                if "DAV" in line:
                    raw_values = line.split()
                    de = float(raw_values[2])
                    rms = float(raw_values[-2])
                    
                    
        if de < ediff and rms < ediffg:
            return True
        else:
            return False
    else:
        return False
    