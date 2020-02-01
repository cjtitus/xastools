from __future__ import division
import numpy as np
from numpy.polynomial import Polynomial as P
def double_jump(e, k, i1, i2, a=1, r=2):
    """
    Normalized double arctan edge jump --- goes from 0 to a
    """
    return a*((r*edge_jump(e, k, i1) + edge_jump(e, k, i2))/(r+1))

def edge_jump(e, k, i1):
    return (np.arctan(k*(e - i1)) + np.pi/2)/np.pi

def fit_preedge(e, c, e1, e2):
    """

    :param e: Energy 
    :param c: Counts 
    :param e1: Start of fit region (energy)
    :param e2: End of fit region (energy)
    :returns: Pre-edge flattened c
    :rtype: 

    """
    idx1 = np.argmin(np.abs(e - e1))
    idx2 = np.argmin(np.abs(e - e2))
    efit = e[idx1:idx2]
    cfit = c[idx1:idx2]
    p = P.fit(efit, cfit, 1)
    return p(e)

def flatten_pre(e, c, e1, e2):
    b = fit_preedge(e, c, e1, e2)
    return c - b

def fit_postedge(e, c, e1, e2, deg):
    idx1 = np.argmin(np.abs(e - e1))
    idx2 = np.argmin(np.abs(e - e2))
    efit = e[idx1:idx2]
    cfit = c[idx1:idx2]
    p = P.fit(efit, cfit, deg)
    return p(e)

def flatten_post(e, c, e0, e1, e2, deg):
    post = fit_postedge(e, c, e1, e2, deg)
    idx = np.argmin(np.abs(e - e0))
    post2 = post - post[idx]
    post2[post2<0] = 0
    scale = post[idx]
    return (c - post2)/scale










    
