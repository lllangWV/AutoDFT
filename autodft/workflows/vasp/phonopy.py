import os
import subprocess

from pymatgen.core import Structure
from autodft.io.vasp import Kpoints
from autodft.workflows.task import BaseTask

import numpy as np
import phonopy
from phonopy import Phonopy
from phonopy.cui.create_force_sets import create_FORCE_SETS
from phonopy.interface.calculator import read_crystal_structure,write_crystal_structure
from phonopy.interface.phonopy_yaml import PhonopyYaml

from autodft.io.vasp import VaspIO
from autodft.workflows.vasp.convergence import check_convergence
from autodft.workflows.vasp.scf import SCFTask

# TODO: create a method to check if the user provided vasp_io object has the required attributes


class PhonopyTask(BaseTask):
    def __init__(self, structure: Structure, base_dir:str=None, vasp_io:VaspIO=None):
        self.structure = structure
        self.base_dir = base_dir
        self.vasp_io = vasp_io
        
    
    def setup(self):
        os.makedirs(self.base_dir, exist_ok=True)
        
        self.structure.to(filename=os.path.join(self.base_dir, "POSCAR"))
        
        
        unitcell, optional_structure_info = read_crystal_structure(os.path.join(self.base_dir,"POSCAR"), 
                                                               interface_mode='vasp')
        
        phonon = Phonopy(unitcell,
                 supercell_matrix=[[2, 0, 0], [0, 2, 0], [0, 0, 2]],
                 primitive_matrix=np.eye(3))
        
        phonon.generate_displacements(distance=0.01)
        
        phonon.save(filename=os.path.join(self.base_dir,"phonopy_params.yaml"), 
                settings= {'displacements': True})
        
        supercells = phonon.supercells_with_displacements
        self.supercells_dir=[]
        self.supercell_tasks=[]
        for i,supercell in enumerate(supercells):
            supercell_dir = os.path.join(self.base_dir,f"{i}")
            self.supercells_dir.append(supercell_dir)
            
            supercell_tuple = supercell.totuple()
            supercell_structure = Structure(
                lattice=supercell_tuple[0],
                species=supercell_tuple[2],
                coords=supercell_tuple[1])
            
            scf_task=SCFTask(structure=supercell_structure, base_dir=supercell_dir, vasp_io=self.vasp_io)
            
            scf_task.setup()
            
            self.supercell_tasks.append(scf_task)

            
            # os.chdir(f'{supercell_dir}')
            # result = subprocess.run(['sbatch', f'run.slurm'], capture_output=False, text=True)

    
    def run(self):
        for task in self.supercell_tasks:
            task.run()
    
    def postprocess(self):
        self.create_force_sets(disp_filename=os.path.join(self.base_dir,"phonopy_params.yaml"), 
                               force_sets_filename=os.path.join(self.base_dir,"FORCE_SETS"))

    
    def create_force_sets(self, disp_filename:str, force_sets_filename:str):
        print("Force sets do not exist. Trying to creating them.")
    
        phonon = phonopy.load(disp_filename)
        phpy_yaml = PhonopyYaml()
        phpy_yaml.read(disp_filename)
        
        force_filenames=[]
        for i,supercell_dir in enumerate(self.supercells_dir):
            filename=os.path.join(supercell_dir,'vasprun.xml')
            force_filenames.append(filename)
            
        create_FORCE_SETS(interface_mode='vasp', force_filenames=force_filenames,
                        phpy_yaml = phpy_yaml,
                        disp_filename=os.path.join(self.base_dir,"phonopy_params.yaml"), 
                        force_sets_filename =force_sets_filename)