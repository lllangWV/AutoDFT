import os
import subprocess


from pymatgen.core import Structure
from autodft.io.vasp import VaspIO
from autodft.workflows.task import BaseTask

from autodft.io.vasp import Incar, Kpoints
from autodft.workflows.vasp.convergence import check_convergence

# TODO: create method to automatically determine NCORE
scf_incar_params = {
    
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


scf_kpoints_params = {
    'type': 'gamma',
    'grid': (9, 9, 9),
    'shift': (0, 0, 0),
}

class SCFTask(BaseTask):
    def __init__(self, structure: Structure, base_dir: str='.', vasp_io:VaspIO=None):
        self.structure = structure
        self.base_dir = base_dir
        
        self.vasp_io = vasp_io
        if self.vasp_io is None:
            scf_incar = Incar(params  = scf_incar_params)
            scf_kpoints = Kpoints(structure = self.structure, params = scf_kpoints_params)
            self.vasp_io = VaspIO(self.structure, incar = scf_incar, kpoints = scf_kpoints)
            
    def setup(self):
        os.makedirs(self.base_dir, exist_ok=True)
        is_converged = check_convergence(self.base_dir, 
                                             ediff=self.vasp_io.incar.EDIFF, 
                                             ediffg=self.vasp_io.incar.EDIFFG)
            
        if is_converged:
            print(f"Skipping {self.base_dir} because it is already converged")
            return None
        
        self.vasp_io.poscar.write(os.path.join(self.base_dir, 'POSCAR'))
        self.vasp_io.potcar.write(os.path.join(self.base_dir, 'POTCAR'))
        self.vasp_io.incar.write(os.path.join(self.base_dir, 'INCAR'))
        self.vasp_io.kpoints.write(os.path.join(self.base_dir, 'KPOINTS'))
        return None
        
    def run(self):
        
        
        os.chdir(f'{self.base_dir}')
        result = subprocess.run(['sbatch', f'run.slurm'], capture_output=False, text=True)