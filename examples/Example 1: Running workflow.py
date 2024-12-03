
import os


from autodft.workflows.vasp import SCFTask
from autodft.workflows.vasp import NonSCFTask
from pymatgen.core import Structure

structure = Structure.from_file(os.path.join('data','Ti3Au','223','POSCAR'))

scf_task = SCFTask(structure)
nscf_task = NonSCFTask(structure)

base_dir = os.path.dirname(os.path.abspath(__file__))

scf_task.run()
nscf_task.run()




tasks= []