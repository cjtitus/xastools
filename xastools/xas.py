import numpy as np
import xarray as xr
from six import string_types
import matplotlib.pyplot as plt
from xastools.utils import (find_mono_offset, correct_mono)
from .io.exportTools import convertDataHeader


class XAS:
    scaninfokeys = ['motor', 'scan', 'date', 'sample', 'loadid', 'command']

    @classmethod
    def from_data_header(cls, data, header):
        """
        Create an XAS object from a 2-d numpy array and a dictionary
        that contains "scaninfo", "channelinfo", and "motors" sub-dictionaries
        """
        arr, h = convertDataHeader(data, header)
        return cls(arr, **h)

    def __init__(self, data, scaninfo={}, motors={}, channelinfo={}):
        for k in self.scaninfokeys:
            setattr(self, k, scaninfo.get(k, None))
        self.bintype = 'XAS'
        self.data = data.copy(deep=True)
        self.motors = motors
        self.scaninfo = {}
        for k in scaninfo:
            if k not in self.scaninfokeys:
                self.scaninfo[k] = scaninfo[k]
        self.channelinfo = channelinfo

    def __eq__(self, y):
        for k in self.scaninfokeys:
            if not np.all(getattr(self, k, None) == getattr(y, k, None)):
                return False
        if not np.all(self.data == y.data):
            return False
        return True

    def getHeader(self):
        scaninfo = {k: getattr(self, k, None) for k in self.scaninfokeys}
        scaninfo.update(getattr(self, 'scaninfo', {}))
        motors = getattr(self, 'motors', {})
        header = {'scaninfo': scaninfo, 'motors': motors, 'channelinfo': self.channelinfo}
        return header

    def __add__(self, y):
        if y is None:
            return self.copy()
        if y.bintype != self.bintype:
            raise TypeError("Cannot add %s to %s" % (y.bintype, self.bintype))
        header = self.getHeader()
        data = xr.concat([self.data, y.data], "scan")
        return XAS(data, **header)

    def __iadd__(self, y):
        if y is None:
            return self
        if y.bintype != self.bintype:
            raise TypeError("Cannot add %s to %s" % (y.bintype, self.bintype))
        self.data = xr.concat([self.data, y.data], "scan")
        return self

    """ 
    def __getitem__(self, key):
        if key not in self.cols:
            raise KeyError
        else:
            idx = self.cols.index(key)
            return np.squeeze(self.data[:, idx, ...].copy())
    """

    def copy(self):
        data = self.data.copy()
        header = self.getHeader()
        return XAS(data, **header)

    def getWeights(self, cols):
        weights = self.data.weights.sel(ch=cols).copy()
        return weights.fillna(1)

    def getOffsets(self, cols):
        offsets = self.data.offsets.sel(ch=cols).copy()
        return offsets.fillna(0)

    def getCols(self, cols):
        """
        Returns a copy of the data object with the chosen columns
        """

        return self.data.data.sel(ch=cols).copy()

    def getData(self, cols, divisor=None, xcol='MONO', individual=False,
                offset=False, offsetMono=False, return_x=True,
                weight=False, squeeze=True):
        """FIXME! briefly describe function

        :param cols: 
        :param divisor: columns to use to divide all the data
        :param x: 
        :param individual: 
        :returns: x, data1, data2, ...
        :rtype: 

        """
        x = self.getCols(xcol)
        y = self.getCols(cols)

        if offset:
            o = self.getOffsets(cols)
            y -= o
        if weight:
            w = self.getWeights(cols)
            y /= w
        if divisor is not None:
            # wtf was this doing??
            # div = np.cumprod(self.getCols(divisor), axis=1)[:, [-1], ...]
            div = self.getCols(divisor)
            y /= div

        if offsetMono:
            deltaE = self.getOffsets('MONO')
            for n in range(len(y.scan)):
                ytmp = y[{"scan": n}]
                dE = deltaE[{"scan": n}]
                xtmp = x[{"scan": n}]
                y[{"scan": n}] = correct_mono(xtmp, dE, ytmp)

        if not individual:
            x = x.mean(dim='scan')
            y = y.sum(dim='scan')

        if squeeze:
            x = x.squeeze()
            y = y.squeeze()

        if return_x:
            return x, y
        else:
            return y

    def plot(self, col, individual=False, nstack=7, **kwargs):
        """See getData for all kwargs

        :param col: 
        :param individual: 
        :param nstack: 
        :param offsetMono:
        :param offset:
        :returns: figure, axis (or list of figures and axes)
        :rtype: 

        """

        x, data = self.getData(col, individual=individual, **kwargs)
        if individual:
            for n, s in enumerate(data.scan.data):
                if n % nstack == 0:
                    if n != 0:
                        plt.legend()
                    else:
                        figlist = []
                        axlist = []
                    fig = plt.figure()
                    ax = fig.add_subplot(111)
                    figlist.append(fig)
                    axlist.append(ax)
                ax.plot(x.sel(scan=s), data.sel(scan=s), label=f"Scan {s}")
            ax.legend()
            return figlist, axlist
        else:
            fig = plt.figure()
            ax = fig.add_subplot(111)
            ax.plot(x, data, label=col)
            ax.legend()
        return fig, ax

    def setMonoOffset(self, deltaE):
        self.data['offsets'].loc[dict(ch="MONO")] = deltaE

    def findMonoOffset(self, edge, col='REF', width=5, **kwargs):
        """
        edge : String or number, passed to find_mono_offset
        col : Column to use for alignment
        width : width of alignment window
        **kwargs : passed to getData
        """
        x, y = self.getData(col, individual=True, **kwargs)
        deltaE = find_mono_offset(x.data, y.data, edge, width)
        self.setMonoOffset(deltaE)
        return deltaE

    def checkMonoOffset(self, col='REF', nstack=14, vline=None):
        figlist, axlist = self.plot(col, individual=True, offsetMono=True,
                                    nstack=nstack)
        if vline:
            for ax in axlist:
                ax.axvline(vline)
        return figlist, axlist
