import numpy as np

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

def areaNorm(x, y):
    """
    :param x: X-coordinates of data
    :param y: Y-coordinates of data
    :returns: y with total area normalized to 1
    :rtype: 

    """
    area = np.trapz(y, x)
    if len(y.shape) == 2:
        area = area.reshape((area.shape[0], 1))

    return y/area

def tailNorm(y):
    """
    tailNorm essentially sets the pre-edge to 0, and the post-edge to 1.
    It works just like ppNorm, but for "min" uses the average of the first 10
    points, and for max uses the average of the last 10 points.
    
    :param y: y data (counts)
    
    """
    ymin = np.mean(y[:10])
    ymax = np.mean(y[-10:])
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
        return ppNorm(y, ylow, yhigh)
    elif normType == "area":
        return areaNorm(x, y, ylow, yhigh)
    elif normType == "tail":
        return tailNorm(y, ylow, yhigh)
    else:
        return y
