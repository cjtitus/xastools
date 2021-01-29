import numpy as np
from scipy.interpolate import UnivariateSpline
from scipy.signal import savgol_filter, argrelmax

refEdges = {'o': 527, 'mn':638, 'fe':706.9, 'co':779.1, 'ni':852.7}

def at_least_2d(arr):
    if len(arr.shape) < 2:
        return arr[:, np.newaxis]
    else:
        return arr
    
def appendMatrices(*args):
    data = np.dstack(list(map(np.atleast_3d, args)))
    return data

def appendArrays(*args):
    data = np.concatenate(list(map(at_least_2d, args)), axis=-1)
    return data

def appendVectors(*args):
    data = np.hstack(args)
    return data

def ppNorm(y):
    """

    :param x: X-coordinates of data
    :param y: Y-coordinates of data
    :param ylow: optional, lower error bound
    :param yhigh: optional, upper error bound
    :returns: y with min(y) set to 0 and max(y) set to 1
    :rtype: 

    """
    ymin = np.min(y, axis=-1, keepdims=True)
    ymax = np.max(y, axis=-1, keepdims=True)
    ynorm = (y - ymin)/(ymax - ymin)

    return ynorm

def areaNorm(x, y, start=0, end=None, offset=True):
    """
    :param x: X-coordinates of data
    :param y: Y-coordinates of data
    :returns: y with total area normalized to 1
    :rtype: 

    """
    if offset:
        sub = np.mean(y[start:start+10, ...], axis=0)
    else:
        sub = 0
    area = np.trapz(y[start:end, ...] - sub, x[start:end, ...])
    if len(y.shape) == 2:
        area = area.reshape((area.shape[0], 1))

    return (y - sub)/area

def tailNorm(y, start=0, end=-10):
    """
    tailNorm essentially sets the pre-edge to 0, and the post-edge to 1.
    It works just like ppNorm, but for "min" uses the average of the first 10
    points, and for max uses the average of the last 10 points.
    
    :param y: y data (counts)
    
    """
    ymin = np.mean(y[start:start + 10])
    if end < 0:
        end = len(y) + end
    ymax = np.mean(y[end:end + 10])
    ynorm = (y - ymin)/(ymax - ymin)

    return ynorm
    
def normalize(x, y, normType):
    """Dispatch function for other normalization functions

    :param x: 
    :param y: 
    :param normType: 
    :returns: 
    :rtype: 

    """
    if normType == "pp":
        return ppNorm(y)
    elif normType == "area":
        return areaNorm(x, y)
    elif normType == "tail":
        return tailNorm(y)
    else:
        return y

def correct_mono(mono, offset, scancounts):
    scancounts_new = np.zeros_like(scancounts)
    if len(scancounts.shape) == 2:
        for n in range(scancounts.shape[1]):
            count_f = UnivariateSpline(mono + offset[n], scancounts[:, n], 
                                       s=0, k=1, ext=3)
            scancounts_new[:, n] = count_f(mono)
    else:
        count_f = UnivariateSpline(mono + offset, scancounts,
                                   s=0, k=1, ext=3)
        scancounts_new = count_f(mono)
    return scancounts_new

def find_mono_offset(xlist, ylist, edge, width=5, smooth=False):
    """
    Default alignment method for data that has a good peak
    xlist.shape = (npts, nscans)
    ylist.shape = (npts, nscans)
    """
    if edge in refEdges:
        nominal = refEdges[edge]
    else:
        try:
            nominal = float(edge)
        except:
            print("Could not understand edge ")
    if len(xlist.shape) > 1:
        xlist = xlist[:, 0]
    if len(ylist.shape) == 1:
        ylist = np.expand_dims(ylist, axis=1)
    xidx = (xlist > (nominal - width)) & (xlist < (nominal + width))
    x = xlist[xidx]

    if smooth:
        ysmooth = savgol_filter(ylist, 15, 2, axis=0)
        y = ysmooth[xidx, :]
    else:
        y = ylist[xidx, :]
    xdelta = []
    for n in range(y.shape[1]):
        xmax = x[np.argmax(y[:, n])]
        spline = UnivariateSpline(x, y[:, n], ext=3, s=0)
        xdense = np.linspace(xmax-1, xmax+1, 100)
        xdelta.append(nominal - xdense[np.argmax(spline(xdense))])
    meanDelta = np.mean(xdelta)
    if np.std(xdelta) > 0.3:
        print("High standard dev on alignment")
    if np.abs(meanDelta) > 0.5:
        print("High mean delta, check alignment")
    return np.array(xdelta)

