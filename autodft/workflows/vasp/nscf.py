from pymatgen.core import Structure
from autodft.io.vasp import Kpoints
from autodft.workflows.task import BaseTask
class NonSCFTask(BaseTask):
    def __init__(self, structure: Structure):
        self.structure = structure
        self.kpoints = Kpoints(structure)
        
    def run(self):
        pass