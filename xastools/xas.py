import numpy as np
from copy import copy
from six import string_types
import matplotlib.pyplot as plt
import datetime
from xastools.utils import find_mono_offset, correct_mono, appendMatrices, appendArrays, appendVectors
from xastools.read import writeSSRL, readSSRL

def file2spectrum(filename, bintype='xas'):
    data, header = readSSRL(filename)
    return XAS(data, bintype=bintype, **header)

def files2spectrum(filenames, bintype='xas'):
    spectra = [file2spectrum(filename, bintype) for filename in filenames]
    spectra.sort(key=lambda x: x.scans)
    return reduce(lambda x, y: x + y, spectra)


class XAS:
    def __init__(self, data, sample=None, scan=None, cols=None, offsets=None, weights=None, **kwargs):
        self.bintype = 'XAS'
        self.sample = sample
        self.scans = np.array(scan, dtype=np.int)
        self.data = np.array(data)
        self.cols = cols
        self.offsets = np.array(offsets, dtype=np.float)
        self.weights = np.array(weights, dtype=np.float)

    def __add__(self, y):
        if y == None:
            return self.copy()
        if y.bintype != self.bintype:
            raise TypeError("Cannot add %s to %s"%(y.bintype, self.bintype))
        data = appendMatrices(self.data, y.data)
        weights = appendArrays(self.weights, y.weights)
        offsets = appendArrays(self.offsets, y.offsets)
        scans = appendVectors(self.scans, y.scans)
        return XAS(data, self.bintype, self.sample, scans, self.cols, offsets, weights)

    def __iadd__(self, y):
        if y == None:
            return self
        if y.bintype != self.bintype:
            raise TypeError("Cannot add %s to %s"%(y.bintype, self.bintype))
        self.data = appendMatrices(self.data, y.data)
        self.weights = appendArrays(self.weights, y.weights)
        self.offsets = appendArrays(self.offsets, y.offsets)
        self.scans = appendVectors(self.scans, y.scans)
        return self

    def __getitem__(self, key):
        if key not in self.cols:
            raise KeyError
        else:
            idx = self.cols.index(key)
            return np.squeeze(self.data[:, idx, ...].copy())
        
    def copy(self):
        data = self.data.copy()
        weights = self.weights.copy()
        offsets = self.offsets.copy()
        scans = self.scans.copy()
        cols = copy(cols)
        return XAS(data, self.bintype, self.sample, scans, cols, offsets, weights)

    def getColIdx(self, cols):
        if not isinstance(cols, string_types):
            idx = [self.cols.index(c) for c in cols]
        else:
            idx = [self.cols.index(cols)]
        return idx
    
    def getWeights(self, cols):
        idx = self.getColIdx(cols)
        weights = self.weights[idx]
        return weights
        
    def getOffsets(self, cols):
        idx = self.getColIdx(cols)
        offsets = self.offsets[idx]
        return offsets

    def getCols(self, cols):
        """
        Returns a copy of the data object with the chosen columns
        """
        idx = self.getColIdx(cols)
        return self.data[:, idx, ...].copy()
    
    def getData(self, cols, divisor=None, xcol='MONO', individual=False, offset=False, offsetMono=False, return_x = True, weight=False, squeeze=True):
        """FIXME! briefly describe function

        :param cols: 
        :param divisor: columns to use to divide all the data
        :param x: 
        :param individual: 
        :returns: x, data1, data2, ...
        :rtype: 

        """
        x = self[xcol]
        if len(x.shape) == 2:
            x = x[:, 0]
        y = self.getCols(cols)

        if offsetMono:
            deltaE = self.getOffsets('MONO')
            if len(y.shape) == 3:
                for n in range(y.shape[-1]):
                    y[..., n] = correct_mono(x, deltaE[..., n], y[..., n])
        if offset:
            o = self.getOffsets(cols)
            y -= o[np.newaxis, ...]
        if weight:
            w = self.getWeights(cols)
            y /= w[np.newaxis, ...]
        if divisor is not None:
            div = np.cumprod(self.getCols(divisor), axis=1)[:, [-1], ...]
            y /= div
        
        if not individual and self.scans.size > 1:
            y = np.sum(y, axis=-1)

        if squeeze:
            y = np.squeeze(y)
            
        if return_x:
            return x, y
        else:
            return y

    def plot(self, col, individual=False, nstack=7, **kwargs):
        x, data = self.getData(col, individual=individual, **kwargs)
        if individual:
            scans = self.scans
            for n in range(data.shape[-1]):
                if n%nstack==0:
                    if n != 0:
                        plt.legend()
                    else:
                        figlist = []
                        axlist = []
                    fig = plt.figure()
                    ax = fig.add_subplot(111)
                    figlist.append(fig)
                    axlist.append(ax)
                ax.plot(x, data[..., n], label=scans[n])
            ax.legend()
            return figlist, axlist
        else:
            fig = plt.figure()
            ax = fig.add_subplot(111)
            ax.plot(x, data, label=col)
            ax.legend()        
        return fig, ax
    
    def writeSSRL(self, filename, date=None, sample='sample', loadid='0', cmd='cmd', slits=None, manip=None, norm='I0', offsetMono=False):
        if self.scans.size > 1:
            scan = int(self.scans[0])
            weights = self.weights[0, :]
            offsets = self.offsets[0, :]
        else:
            scan = int(self.scans)
            weights = self.weights
            offsets = self.offsets
        sample = self.sample
        cols = self.cols
        if norm is not None:
            i0 = self[norm]
            data = self.data.copy()
            data[:, 3:, ...] = np.mean(i0, axis=0)[np.newaxis, np.newaxis, ...]*self.getData(self.cols[3:], offsetMono=offsetMono, return_x=False, individual=True)/i0[:, np.newaxis, ...]
        if len(data.shape) > 2:
            data = np.mean(data, axis=-1)
        if offsetMono:
            c1 = "Mono corrected"
        else:
            c1 = ""
        writeSSRL(filename, cols, data, date=date, sample=sample, loadid=loadid, scan=scan, weights=weights, offsets=None, c1=c1)

    def setMonoOffset(self, deltaE):
        mono_idx = self.getColIdx('MONO')
        for n, E in enumerate(deltaE):
            self.offsets[mono_idx, n] = E

    def findMonoOffset(self, edge, col='REF', width=5):
        x = self['MONO']
        y = self[col]
        deltaE = find_mono_offset(x, y, edge, width)
        self.setMonoOffset(deltaE)

    def checkMonoOffset(self, col='REF', nstack=14, vline=None):
        figlist, axlist = self.plot(col, individual=True, offsetMono=True, nstack=nstack)
        if vline:
            for ax in axlist:
                ax.axvline(vline)
        return figlist, axlist
