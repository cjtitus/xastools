from copy import copy, deepcopy
from os.path import exists
import numpy as np
import yaml

def load(filename):
    throwErrorIfMissing(filename)
    data = loadData(filename)
    header = loadHeader(filename)
    return XY(data, header)

def throwErrorIfMissing(filename):
    if not exists(filename):
        raise FileNotFoundError

def loadData(filename):
    data = np.loadtxt(filename).T
    if data.size == 0:
        raise ValueError
    return data

def loadHeader(filename):
    headerlines = []
    with open(filename, 'r') as f:
        for line in f:
            if line[0] == '#':
                headerlines.append(line[1:])
            else:
                break
    if len(headerlines) == 0:
        header = {'xcols':['x'], 'ycols':['y']}
    else:
        header = yaml.load('\n'.join(headerlines))
    return header

class XY:
    def __init__(self, data, header):
        self.header = header
        self.data = np.atleast_2d(data)
        self.xlen = len(self.getxCols())
        self.ylen = len(self.getyCols())
        self._checkData()
        
    def _checkData(self):
        if self.data.shape[0] != (self.xlen + self.ylen):
            raise ValueError

    def getxData(self, xcol=None):
        if xcol is None:
            return self.data[:self.xlen, :]
        else:
            xcols = self.getxCols()
            idx = xcols.index(xcol)
            return self.data[idx, :]
    
    def getyData(self, ycol=None):
        if ycol is None:
            return self.data[self.xlen:, :]
        else:
            ycols = self.getyCols()
            idx = ycols.index(ycol)
            return self.data[self.xlen + idx, :]

    def getxCols(self):
        return self.header.get('xcols')

    def getyCols(self):
        return self.header.get('ycols')

    def copy(self):
        data = self.data.copy()
        header = deepcopy(self.header)
        return XY(data, header)

    def __add__(self, y):
        if self.getyCols() != y.getyCols():
            raise ValueError
        newXY = self.copy()
        ydata = newXY.getyData()
        ydata += y.getyData()
        return newXY
    
    def save(self, filename):
        header = yaml.dump(self.header)
        np.savetxt(filename, self.data.T, header=header)
        
