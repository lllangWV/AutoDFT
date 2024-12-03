import os
import subprocess
import shutil
import re




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

kpoints_params = {
    'type': 'gamma',
    'grid': (15, 15, 15),
    'shift': (0, 0, 0),
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
    scf_dir = os.path.join(root_dir, "scf")
    
    
    is_converged = check_if_previous_convergence(scf_dir, 
                                             ediff=incar_params["EDIFF"], 
                                             ediffg=incar_params["EDIFFG"])

    if is_converged:
        print("Previous calculation converged. No need to run.")
        return None
    
    print("Previous calculation did not converge or did not exist. Running new calculation.")
    os.makedirs(scf_dir, exist_ok=True)
    
    with open(os.path.join(root_dir, "POSCAR"), "r") as f:
        lines=f.readlines()
        system_name=lines[0].replace('\n','').strip()
    
    with open(os.path.join(scf_dir, "INCAR"), "w") as f:
        
        f.write(f"system   =  {system_name}\n")
        for key, value in incar_params.items():
            f.write(f"{key} = {value}\n")
        f.write("\n")
        
    with open(os.path.join(scf_dir, "KPOINTS"), "w") as f:
        f.write(f"KPOINTS generated by run_scf.py\n")
        f.write(f"0\n")
        f.write(f"{kpoints_params['type']}\n")
        f.write(f"{' '.join(map(str, kpoints_params['grid']))}\n")
        f.write(f"{' '.join(map(str, kpoints_params['shift']))}\n")
        
    with open(os.path.join(root_dir, "run.slurm"), "r") as f:
        submission_lines=f.readlines()
        submission_lines[1] = f"#SBATCH -J {system_name}_scf\n"
    with open(os.path.join(scf_dir, "run.slurm"), "w") as f:
        f.writelines(submission_lines)
        
        
        
    shutil.copyfile(os.path.join(root_dir,'POTCAR'), os.path.join(scf_dir,'POTCAR'))
    shutil.copyfile(os.path.join(root_dir,'POSCAR'), os.path.join(scf_dir,'POSCAR'))

    os.chdir(f'{scf_dir}')
    result = subprocess.run(['sbatch', f'run.slurm'], capture_output=False, text=True)

                

if __name__ == "__main__":
    main()






