
import os


from autodft.workflows.vasp import SCFTask
from autodft.workflows.vasp import NonSCFTask
from autodft.io.vasp import Potcar
from pymatgen.core import Structure
from pymatgen.symmetry import kpath
import warnings


from phonopy import Phonopy
from phonopy.interface.calculator import read_crystal_structure,write_crystal_structure
import numpy as np

from autodft.workflows.vasp.phonopy import PhonopyTask
from autodft import config


config.potcar_dir = '/scratch/lllang/AtomateDB/PP_Vasp/POT_GGA_PAW_PBE_52'
print(config.potcar_dir)



warnings.simplefilter("ignore", DeprecationWarning)
warnings.simplefilter("ignore", UserWarning)

base_dir= os.path.dirname(__file__)
poscar='/users/lllang/SCRATCH/projects/AutoDFT/data/TiAu/Ti3Au/223/POSCAR'


# unitcell, optional_structure_info = read_crystal_structure(poscar, 
#                                                                interface_mode='vasp')
        
# phonon = Phonopy(unitcell,
#             supercell_matrix=[[2, 0, 0], [0, 2, 0], [0, 0, 2]],
#             primitive_matrix=np.eye(3))

# phonon.generate_displacements(distance=0.01)


# supercells = phonon.supercells_with_displacements

# print(supercells[0])
# print(dir(supercells[0]))

# symbols=supercells[0].get_chemical_symbols()

# supercell_tuple = supercells[0].totuple()
# lattice = supercells[0].get_cell()
# symbols = supercells[0].get_chemical_symbols()
# scaled_positions = supercells[0].get_scaled_positions()


# print(supercell_tuple)
# print(lattice)
# print(symbols)
# print(scaled_positions)

calculation_dir = os.path.join(base_dir, 'phonopy')

structure = Structure.from_file(poscar)
phonopy_task = PhonopyTask(structure=structure, base_dir=calculation_dir)

phonopy_task.setup()



# phonopy_task.run()





# structure = Structure.from_file('/users/lllang/SCRATCH/projects/AutoDFT/data/TiAu/Ti3Au/223/POSCAR')

# root_dir=os.path.dirname(__file__)
# print(structure)
# print(structure.symbol_set)
# # print(structure)
# print(structure.species)

# unique_species = []
# for specie in structure.species:
#     if specie.name not in unique_species:
#         unique_species.append(specie.name)
# print("Unique species in order:", unique_species)

# potcar = Potcar(structure, potcar_dir='/users/lllang/SCRATCH/AtomateDB/PP_Vasp/POT_GGA_PAW_PBE_52')
# potcar.write_potcar(filename=os.path.join(root_dir, 'POTCAR'))
# print(potcar.get_specie_potcars('Ti'))

# kpath_seek = kpath.KPathSeek(structure)
# kpath_latimermunro = kpath.KPathLatimerMunro(structure)
# kpath_setyawan_curtarolo = kpath.KPathSetyawanCurtarolo(structure)
# print(kpath_seek.kpath)
# print(kpath_latimermunro.kpath)
# print(kpath_setyawan_curtarolo.kpath)