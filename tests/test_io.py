from chemlab.core import System, Atom, Molecule
from chemlab.io import DataFile
from chemlab.io.gro import GromacsIO
from chemlab.io.edr import EdrIO
import numpy as np
    
def test_datafile():
    DataFile.add_handler(GromacsIO, 'gro', '.gro')
    df = DataFile("tests/data/cry.gro") # It guesses 
    sys = df.read("system")
    assert sys.n_atoms == 1728


def test_read_pdb():
    df = DataFile('tests/data/3ZJE.pdb')
    s = df.read('system')
    
def test_write_pdb():
    water = Molecule([Atom('O', [0.0, 0.0, 0.0], export={'grotype': 'OW'}),
                      Atom('H', [0.1, 0.0, 0.0], export={'grotype': 'HW1'}),
                      Atom('H', [-0.03333, 0.09428, 0.0], export={'grotype': 'HW2'})],
                      export={'groname': 'SOL'})

    sys = System.empty(200, 3*200, boxsize = 2.0)
    for i in range(200):
        sys.add(water.copy())
    
    df = DataFile('/tmp/dummy.gro')
    df.write("system", sys)
    
def test_read_gromacs():
    '''Test reading a gromacs file'''
    df = DataFile('tests/data/cry.gro')
    s = df.read('system')

def test_write_gromacs():
    water = Molecule([Atom('O', [0.0, 0.0, 0.0], export={'grotype': 'OW'}),
                      Atom('H', [0.1, 0.0, 0.0], export={'grotype': 'HW1'}),
                      Atom('H', [-0.03333, 0.09428, 0.0], export={'grotype': 'HW2'})],
                      export={'groname': 'SOL'})

    sys = System.empty(200, 3*200, boxsize = 2.0)
    for i in range(200):
        sys.add(water.copy())
    
    df = DataFile('/tmp/dummy.gro')
    df.write('system', sys)
    
    df = DataFile('/tmp/dummy.gro')
    sread = df.read('system')
    
    assert all(sread.type_array == sys.type_array)
    
def test_read_edr():
    df = DataFile('tests/data/ener.edr')
    df.read('frames')
    
    dt, temp = df.read('quantity', 'Temperature')
    unit = df.read('units', 'Temperature')
    
    try:
        df.read('quantity', 'NonExistent')
    except:
        pass
