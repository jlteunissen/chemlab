'''Parser for gromacs edr'''
from .iohandler import IOHandler
import numpy as np
import xdrlib
import difflib

class QuantityNotAvailable(Exception):
    pass

class EdrIO(IOHandler):
    can_read = ['frames', 'quantity', 'units', 'avail quantities']
    can_write = []
    
    def __init__(self, filename):
        self.f = filename
        self.processed = False
        
    def read(self, feature, *args):
        
        if not self.processed:
            self.frames = frames = self.process_frames()        
            self.processed = True
        else:
            frames = self.frames
        
        if feature == 'frames':
            return frames
        
        if feature == 'quantity':
            if not args[0]:
                raise Exception('the method read("quantity", arg) requires a quantity to get')
                
            
            quant = args[0]
            
            if quant not in self.props:
                close = difflib.get_close_matches(quant, self.props)
                raise QuantityNotAvailable('Quantity %s not available. Close matches: %s'%
                                           (str(quant), str(close)))
                
            i = self.props.index(quant)
            ret = []
            for f in frames:
                ret.append(f[i][0])
            
            return np.array(self.times), np.array(ret)
            
        if feature == 'units':
            quant = args[0]
            i = self.props.index(quant)
            return self.units[i]
            
        if feature == 'avail quantities':
            return self.props

            
    def process_frames(self):
        
        f = open(self.f).read()
        self.up = xdrlib.Unpacker(f)

        self.times = []
        self.dts = []
        self.frames = []

        self._unpack_start()
        fr = self._unpack_first_frame()
        self.frames.append(fr)
        while True:

            try:
                fr = self._unpack_frame()
            except EOFError:
                break
            self.frames.append(fr)

        return self.frames

    def _unpack_start(self):
        up = self.up
        magic = up.unpack_int()
        if  (magic != -55555):
            raise Exception('Format not supported: magic number -55555 not matching')

        self.version = up.unpack_int()
        
        # Number of properties
        self.nre = up.unpack_int()
        

        self.props = props = []
        self.units = units = []

        # Strings and units of quantities
        for i in range(self.nre):
            prop = up.unpack_string()
            unit = up.unpack_string()
            
            props.append(prop)
            units.append(unit)

    def _unpack_eheader(self):
        up = self.up
        first_real_to_check = -2e10

        # Checking the first real for format
        first_real = up.unpack_double()
        if (first_real != first_real_to_check):
            raise Exception('Format not supported, first real not matching.')


        magic = up.unpack_int()
        if  (magic != -7777777):
            raise Exception('Format not supported, magic number not matching -7777777')

        version = up.unpack_int()
        time = up.unpack_double()
        self.times.append(time)
        
        # This two should give us large int that represent the step number
        min = up.unpack_int()
        maj = up.unpack_int()

        nsum = up.unpack_int()

        # NSTEPS (again?)
        min = up.unpack_int()
        maj = up.unpack_int()

        # For version 5
        dt = up.unpack_double()
        self.dts.append(dt)

        # Number of properties?
        self.nre = up.unpack_int()

        dum = up.unpack_int()

        nblock = up.unpack_int() + 1

        # Block headers:
        id = up.unpack_int()
        nsubblocks = up.unpack_int()

        e_size = up.unpack_int()
        #dum = up.unpack_int()
        #dum = up.unpack_int()
        #up.unpack_int()


    def _unpack_first_frame(self):
        # First unpacking Just the energies
        
        frame = []
        self._unpack_eheader()
        for i in range(self.nre):
            en = self.up.unpack_double()
            # energy, average, rmsd
            frame.append([en, en, 0.0])
        
        return frame
    def _unpack_frame(self):
        # Energies, averages and rmsd
        self._unpack_eheader()
        frame = []
        
        for i in range(self.nre):
            en = self.up.unpack_double()
            avg = self.up.unpack_double()
            rmsd = self.up.unpack_double()
            
            frame.append([en, avg, rmsd])
        return frame