import numpy as np
from copy import copy
from six import string_types
import matplotlib.pyplot as plt
import datetime
from xastools.utils import find_mono_offset, correct_mono, appendMatrices, appendArrays, appendVectors

class RIXS:
    def __init__(self, x, y, z, xas, eoffsets=None, **kwargs):
        self.bintype = 'RIXS'
        self.xas = xas
        self.x = np.array(x)
        self.y = np.array(y)
        self.z = np.array(z)
        if eoffsets is None:
            self.eoffsets = np.zeros_like(self.xas.scans)
        else:
            self.eoffsets = eoffsets

    def __add__(self, other):
        if other == None:
            return self.copy()
        if other.bintype != self.bintype:
            raise TypeError("Cannot add %s to %s"%(other.bintype, self.bintype))
        x = self.x.copy()
        y = self.y.copy()
        z = appendMatrices(self.z, other.z)
        offsets = appendVectors(self.eoffsets, other.eoffsets)
        xas = self.xas + other.xas
        return RIXS(x, y, z, xas, offsets)

    def __iadd__(self, other):
        if other == None:
            return self.copy()
        if other.bintype != self.bintype:
            raise TypeError("Cannot add %s to %s"%(other.bintype, self.bintype))
        self.z = appendMatrices(self.z, other.z)
        self.eoffsets = appendVectors(self.eoffsets, other.eoffsets)
        self.xas += other.xas
        return self

    def copy(self):
        x = self.x.copy()
        y = self.y.copy()
        z = self.z.copy()
        offsets = self.eoffsets.copy()
        xas = self.xas.copy()
        return RIXS(x, y, z, xas, offsets)

    def getData(self, divisor=None, individual=False, offsetMono=False, offsetEnergy=False):
        pass

    

    
