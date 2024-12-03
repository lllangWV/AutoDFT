import os
import subprocess
import shutil
import re

import phonopy
import numpy as np
from phonopy import Phonopy
from phonopy.interface.calculator import read_crystal_structure,write_crystal_structure


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
    "ICHARG": 2,
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
    "LCHARG": False,
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

kpoints_params = {
    'type': 'gamma',
    'grid': (9, 9, 9),
    'shift': (0, 0, 0),
}



def check_if_previous_convergence(dir, ediff, ediffg, convergence_method = None):
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
    
def main():
    

    root_dir = os.path.dirname(os.path.abspath(__file__))
    phonon_dir = os.path.join(root_dir, "phonon")
    
    os.makedirs(phonon_dir, exist_ok=True)
    
    with open(os.path.join(root_dir, "POSCAR"), "r") as f:
        lines=f.readlines()
        system_name=lines[0].replace('\n','').strip()
    
    
    unitcell, optional_structure_info = read_crystal_structure(os.path.join(root_dir,"POSCAR"), 
                                                               interface_mode='vasp')
   

    phonon = Phonopy(unitcell,
                 supercell_matrix=[[2, 0, 0], [0, 2, 0], [0, 0, 2]],
                 primitive_matrix=np.eye(3))
    
    phonon.generate_displacements(distance=0.01)
    
    

    
    supercells = phonon.supercells_with_displacements
    for i,supercell in enumerate(supercells):
    
        supercell_dir = os.path.join(phonon_dir,f"{i}")
        is_converged = check_if_previous_convergence(supercell_dir, 
                                             ediff=incar_params["EDIFF"], 
                                             ediffg=incar_params["EDIFFG"])

        if is_converged:
            print("Previous calculation converged. No need to run.")
            return None
        
        print("Previous calculation did not converge or did not exist. Running new calculation.")
        
        
        os.makedirs(supercell_dir, exist_ok=True)
        write_crystal_structure(os.path.join(supercell_dir, 'POSCAR'), supercell, interface_mode='vasp')
        

        shutil.copyfile(os.path.join(root_dir,'POTCAR'), os.path.join(supercell_dir,'POTCAR'))

        with open(os.path.join(supercell_dir, "KPOINTS"), "w") as f:
            f.write(f"KPOINTS generated by run_phonon.py\n")
            f.write(f"0\n")
            f.write(f"{kpoints_params['type']}\n")
            f.write(f"{' '.join(map(str, kpoints_params['grid']))}\n")
            f.write(f"{' '.join(map(str, kpoints_params['shift']))}\n")
        
        with open(os.path.join(supercell_dir, "INCAR"), "w") as f:
            
            f.write(f"system   =  {system_name}\n")
            for key, value in incar_params.items():
                f.write(f"{key} = {value}\n")
            f.write("\n")
        
        with open(os.path.join(root_dir, "run.slurm"), "r") as f:
            submission_lines=f.readlines()
            submission_lines[1] = f"#SBATCH -J {system_name}_phonon-supercell_{i}\n"
        with open(os.path.join(supercell_dir, "run.slurm"), "w") as f:
            f.writelines(submission_lines)
            
        os.chdir(f'{supercell_dir}')
        result = subprocess.run(['sbatch', f'run.slurm'], capture_output=False, text=True)

            
    phonon.save(filename=os.path.join(phonon_dir,"phonopy_params.yaml"), 
                settings= {'displacements': True})
        

    
                

if __name__ == "__main__":
    main()





