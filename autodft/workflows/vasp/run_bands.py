import os
import subprocess
import shutil
import re



from pymatgen.core import Structure
import seekpath

from autodft.io.vasp import Kpoints

import warnings

# Suppress a specific warning
warnings.filterwarnings("ignore", category=UserWarning)


incar_params = {
    # Precision and convergence settings
    "# Precision and convergence settings": '',
    "PREC": "High",
    "NELMIN": 8,
    "NELM": 100,
    "EDIFF": 1e-08,
    "EDIFFG": -1e-04,
    '# End Precision and convergence settings': '\n',
    
    # Electronic structure settings
    "# Electronic structure settings": '',
    "ISMEAR": 1,
    "SIGMA": 0.05,
    "ISPIN": 2,
    "ICHARG": 11,
    "NEDOS": 300,
    '# End Electronic structure settings': '\n',
    
    # Optimization settings
    "# Optimization settings": '',
    "LREAL": False,
    "NSW": 0,
    "IBRION": -1,
    "ENCUT": 600,
    '# End Optimization settings': '\n',

    # Wavefunction and grid settings
    "# Wavefunction and grid settings": '',
    "LWAVE": False,
    "LASPH": True,
    "LORBIT": 11,
    "LMAXMIX": 4,
    "ADDGRID": True,
    "NWRITE": 3,
    '# End Wavefunction and grid settings': '\n',
    
    # Parallelization parameters
    "# Parallelization parameters": '',
    "NCORE": 20,
    '# End Parallelization parameters': '\n'
}


def check_if_previous_convergence(dir, ediff, ediffg, convergence_method = None):
    oszicar=os.path.join(dir,'OSZICAR')

    if os.path.exists(oszicar):
        "aborting loop because EDIFF is reached"
        
        with open(oszicar) as f:
            lines = f.readlines()
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
    
    


def main():
    

    root_dir = os.path.dirname(os.path.abspath(__file__))
    bands_dir = os.path.join(root_dir, "bands")
    scf_dir = os.path.join(root_dir, "scf")
    with_time_reversal=True
    
    
    is_converged = check_if_previous_convergence(bands_dir, 
                                             ediff=incar_params["EDIFF"], 
                                             ediffg=incar_params["EDIFFG"])

    if is_converged:
        print("Previous calculation converged. No need to run.")
        return None
    
    print("Previous calculation did not converge or did not exist. Running new calculation.")
    os.makedirs(bands_dir, exist_ok=True)
    
    
    if os.path.exists(os.path.join(scf_dir,'CHGCAR')):
        shutil.copyfile(os.path.join(scf_dir,'CHGCAR'), os.path.join(bands_dir,'CHGCAR'))
    else:
        raise FileNotFoundError("Self-consistent calculation not found. Please run run_scf.py first.")


    with open(os.path.join(root_dir, "POSCAR"), "r") as f:
        lines=f.readlines()
        system_name=lines[0].replace('\n','').strip()
    
    with open(os.path.join(scf_dir, "INCAR"), "w") as f:
        
        f.write(f"system   =  {system_name}\n")
        for key, value in incar_params.items():
            f.write(f"{key} = {value}\n")
        f.write("\n")
    
    kpoints_string = get_kpath(os.path.join(root_dir, 'POSCAR'),with_time_reversal=with_time_reversal)
    
    with open(os.path.join(bands_dir, "KPOINTS"), "w") as f:
        f.write(kpoints_string)
        
    with open(os.path.join(root_dir, "run.slurm"), "r") as f:
        submission_lines=f.readlines()
        submission_lines[1] = f"#SBATCH -J {system_name}_bands\n"
    with open(os.path.join(bands_dir, "run.slurm"), "w") as f:
        f.writelines(submission_lines)
        
    shutil.copyfile(os.path.join(root_dir,'POTCAR'), os.path.join(bands_dir,'POTCAR'))
    shutil.copyfile(os.path.join(root_dir,'POSCAR'), os.path.join(bands_dir,'POSCAR'))

    os.chdir(f'{bands_dir}')
    result = subprocess.run(['sbatch', f'run.slurm'], capture_output=False, text=True)

                

if __name__ == "__main__":
    main()






