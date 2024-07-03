import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from xastools.utils import (find_mono_offset, correct_mono, normalize)

def inferColTypes(cols):
    motorNames = ['Seconds', 'ENERGY_ENC', 'MONO']
    sensorNames = ['TEMP']
    coltypes = []
    for c in cols:
        if c in motorNames:
            coltypes.append('motor')
        elif c in sensorNames:
            coltypes.append('sensor')
        else:
            coltypes.append('detector')
    return coltypes

def convertDataHeader(data, header):
    scan = header['scaninfo'].pop('scan', None)
    cols = header['channelinfo']['cols']
    offsets = header['channelinfo'].pop('offsets', {})
    weights = header['channelinfo'].pop('weights', {})
    if "coltypes" not in header['channelinfo']:
        coltypes = np.array(inferColTypes(cols))
        header['channelinfo']['coltypes'] = coltypes
    x = xr.DataArray(data, dims=['index', 'ch'], coords={'ch': cols})
    offset_cols = list(offsets.keys())
    offset_data = np.array([offsets[k] for k in offset_cols])
    o = xr.DataArray(offset_data, dims=["ch"], coords=[offset_cols])
    weight_cols = list(weights.keys())
    weight_data = np.array([weights[k] for k in weight_cols])
    w = xr.DataArray(weight_data, dims=["ch"], coords=[weight_cols])
    d = xr.Dataset({"data": x, "offsets": o, "weights": w})

    if isinstance(scan, int):
        d = d.expand_dims({"scan": [scan]})
    else:
        d = d.expand_dims({"scan": [scan[0]]})
    return d, header

class XAS:
    scaninfokeys = ['motor', 'date', 'sample', 'loadid', 'command']

    @classmethod
    def from_data_header(cls, data, header):
        """
        Create an XAS object from a 2-d numpy array and a dictionary
        that contains "scaninfo", "channelinfo", and "motors" sub-dictionaries
        """
        arr, h = convertDataHeader(data, header)
        return cls(arr, **h)

    def __init__(self, data, scaninfo={}, motors={}, channelinfo={}, **kwargs):
        """Create an XAS object directly from a properly formatted xarray, 
        and three metadata dictionaries
        """
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

    @property
    def columns(self):
        return tuple(self.channelinfo['cols'])

    def getHeader(self):
        scaninfo = {k: getattr(self, k, None) for k in self.scaninfokeys}
        scaninfo.update(getattr(self, 'scaninfo', {}))
        motors = getattr(self, 'motors', {})
        header = {'scaninfo': scaninfo, 'motors': motors,
                  'channelinfo': self.channelinfo}
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

    def getIncludedScans(self, exclude):
        scans = list(self.data.data.scan.data)
        if type(exclude) == int:
            exclude = [exclude]
        for s in exclude:
            scans.pop(scans.index(s))
        return scans

    def getWeights(self, cols, exclude=[]):
        scans = self.getIncludedScans(exclude)
        weights = self.data.weights.sel(ch=cols, scan=scans).copy()
        return weights.fillna(1)

    def getOffsets(self, cols, exclude=[]):
        scans = self.getIncludedScans(exclude)
        offsets = self.data.offsets.sel(ch=cols, scan=scans).copy()
        return offsets.fillna(0)

    def getCols(self, cols, exclude=[]):
        """
        Returns a copy of the data object with the chosen columns
        """
        scans = self.getIncludedScans(exclude)
        return self.data.data.sel(ch=cols, scan=scans).copy()

    def getData(self, cols, divisor=None, xcol='MONO', individual=False,
                offset=False, offsetMono=False, return_x=True,
                weight=False, squeeze=True, aggregate='sum', exclude=[]):
        """FIXME! briefly describe function

        :param cols: 
        :param divisor: columns to use to divide all the data
        :param x: 
        :param individual: 
        :returns: x, data1, data2, ...
        :rtype: 

        """
        x = self.getCols(xcol, exclude)
        y = self.getCols(cols, exclude)

        if offset:
            o = self.getOffsets(cols, exclude)
            y = y-o
        if weight:
            w = self.getWeights(cols, exclude)
            y = y/w
        if divisor is not None:
            # wtf was this doing??
            # div = np.cumprod(self.getCols(divisor), axis=1)[:, [-1], ...]
            div = self.getCols(divisor)
            y = y/div

        if offsetMono:
            deltaE = self.getOffsets('MONO')
            for n in range(len(y.scan)):
                ytmp = y[{"scan": n}]
                dE = deltaE[{"scan": n}]
                xtmp = x[{"scan": n}]
                y[{"scan": n}] = correct_mono(xtmp, dE, ytmp)

        if not individual:
            x = x.mean(dim='scan')
            if aggregate == 'sum':
                y = y.sum(dim='scan')
            elif aggregate == 'mean':
                y = y.mean(dim='scan')

        if squeeze:
            x = x.squeeze()
            y = y.squeeze()

        if return_x:
            return x, y
        else:
            return y

    def plot(self, col, individual=False, nstack=7, ax=None, label=None,
             normType=None, titlefmt="{sample} {scaninfo[element]} XAS", **kwargs):
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
        title = titlefmt.format(**self.__dict__)
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
                xsel = x.sel(scan=s).data
                ysel = data.sel(scan=s).data
                ax.plot(xsel, normalize(xsel, ysel, normType),
                        label=f"Scan {s}")
            ax.legend()
            ax.set_title(title)
            return figlist, axlist
        else:
            if ax is None:
                fig = plt.figure()
                ax = fig.add_subplot(111)
            else:
                fig = ax.get_figure()
            if label is None:
                label = col
            x = x.data
            data = data.data
            ax.plot(x, normalize(x, data, normType), label=label)
            ax.legend()
            ax.set_title(title)
        return fig, ax

    def setMonoOffset(self, deltaE):
        self.data['offsets'].loc[dict(ch="MONO")] = deltaE

    def findMonoOffset(self, edge, col='REF', width=5, smooth=False, shift=0, **kwargs):
        """
        edge : String or number, passed to find_mono_offset
        col : Column to use for alignment
        width : width of alignment window
        **kwargs : passed to getData
        """
        x, y = self.getData(col, individual=True, **kwargs)
        deltaE = find_mono_offset(x.data, y.data, edge, width, smooth, shift)
        self.setMonoOffset(deltaE)
        return deltaE

    def checkMonoOffset(self, col='REF', nstack=14, vline=None):
        figlist, axlist = self.plot(col, individual=True, offsetMono=True,
                                    nstack=nstack)
        if vline:
            for ax in axlist:
                ax.axvline(vline)
        return figlist, axlist
