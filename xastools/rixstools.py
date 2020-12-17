import matplotlib.path as mplpath
import numpy as np
from scipy.interpolate import UnivariateSpline

def maskRegion(data, points, invert=False):
    region = mplpath.Path(points, closed=True)
    if len(data['x'].shape) > 1:
        xx = data['x']
        yy = data['y']
    else:
        xx, yy = np.meshgrid(data['x'], data['y'])
    pts = np.vstack([xx.flat, yy.flat]).T
    mask = region.contains_points(pts)
    if invert:
        mask = np.logical_not(mask)
    mask = mask.reshape(xx.shape)    
    zn = data['z'].copy()
    zn[mask] = 0
    return zn

def maskPFYRegion(data, region, **kwargs):
    zn = maskRegion(data, region, **kwargs)
    return np.sum(zn, axis=0)

def fitElastic(data, pfyRegion, elasticRegion, xllim, xulim, weight=True, poly=False, deg=3):
    elastic = maskPFYRegion(data, elasticRegion, invert=True)
    if len(data['x'].shape) > 1:
        x = data['x'][0, :]
    else:
        x = data['x']
    idx = np.logical_or((x < xllim), (x > xulim))
    xelastic = x[idx]
    yelastic = elastic[idx]
    if weight:
        w = 1.0/np.sqrt(yelastic)
    else:
        w = None
    if poly:
        pfit = np.polyfit(xelastic, yelastic, deg, w=w)
        s = np.poly1d(pfit)
    else:
        s = UnivariateSpline(xelastic, yelastic, w=w, k=deg)
    y = maskPFYRegion(data, pfyRegion, invert=True)
    return (x, y, s(x))

def makeBox(x1, y1, x2, y2):
    """
    Makes a box via lower left (x1, y1) and upper right (x2, y2) points
    """
    return [(x1, y1), (x2, y1), (x2, y2), (x1, y2), (x1, y1)]

def makeTrap(x1, y1, x2, y2, width):
    """
    Makes a trapezoid along the given line, with a given width
    in the y-direction
    """
    return [(x1, y1 - width), (x2, y2 - width), (x2, y2 + width), (x1, y1 + width), (x1, y1 - width)]
