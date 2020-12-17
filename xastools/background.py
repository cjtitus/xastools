from __future__ import division
import numpy as np
from scipy.special import erf
from numpy.polynomial import Polynomial as P

def double_jump(e, k, i1, i2, a=1, r=2, f='erf'):
    """
    Normalized double arctan edge jump --- goes from 0 to a
    """
    return a*((r*edge_jump(e, k, i1, f) + edge_jump(e, k, i2, f))/(r+1))

def edge_jump(e, k, i1, f='erf'):
    if f == 'arctan':
        return (np.arctan(k*(e - i1)) + np.pi/2)/np.pi
    elif f == 'erf':
        return 0.5*(erf(k*(e - i1)) + 1)
    else:
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
    """Fits a polynomial of degree deg to post-edge of an XAS spectrum and 
    then flattens it.

    :param e: energy (x)
    :param c: spectrum (y)
    :param e0: Edge position (energy)
    :param e1: Lower limit of fit region (energy)
    :param e2: Upper limit of fit region (energy)
    :param deg: Polynomial degree
    :returns: Post-edge flattened spectrum
    :rtype: 

    """
    post = fit_postedge(e, c, e1, e2, deg)
    idx = np.argmin(np.abs(e - e0))
    post2 = post - post[idx]
    post2[post2<0] = 0
    scale = post[idx]
    return (c - post2)/scale

def lls(data):
    return np.log(np.log(np.sqrt(data + 1) + 1) + 1)

def lls_inv(data):
    tmp = np.exp(np.exp(data) - 1) - 1
    return tmp*tmp - 1

def lsdf(data, fwhm, f=1.5, A=75, M=10, ratio=1.3):
    """
    Low-statistics digital filter
    Translated from pymca
    
    :param data: data to smooth
    :param fwhm: maximum smooth width
    :param f: conversion between FWHM and points
    :param A: Averaging param
    :param M: Threshold for averaging
    :param ratio: acceptance parameter for averaging

    `A`, `M`, `ratio` control smoothing. fwhm and f control the maximum smooth width, and just need to be "large enough" without being too large. 

    `M` controls the typical smoothing. If the entire smooth window sum is < `M`, the midpoint is replaced by the average, effectively controlling window size. If data points > M/3, averaging can only takes place on flat slopes. If you want to smooth when there are 100 counts/bin on the steep side of a peak, you need M > 300.

    `ratio` controls the definition of flat regions for more aggressive averaging. If the Left/Right ratio is flatter than `ratio`, averaging takes place via `A`, allowing a larger region to be averaged than via `M`. 

    `A` is the special averaging parameter for flat ground. It is essentially equal to the desired SNR for the new averaged point, assuming poisson statistics. Roughly, N*S/sqrt(S) < A, where S is the counts in one bin, and N is the averaging window.
    """
    width = int(f*fwhm)
    dout = np.copy(data)
    size = len(dout)
    for channel in range(width, size - width):
        i = width
        while i > 0:
            L = 0
            R = 0
            for j in range(channel - i, channel):
                L += dout[j]
            for j in range(channel + 1, channel + i + 1):
                R += dout[j]
            S = dout[channel] + L + R
            if (S<M):
                dout[channel] = S/(2*i+1)
                break
            dhelp = (R+1)/(L+1)
            if ((dhelp < ratio) and (dhelp > (1.0/ratio))):
                if (S<(A*np.sqrt(data[channel]))):
                    dout[channel] = S/(2*i+1)
                    break
            i = i-1
    return dout

def itersnip(data, snip_width, nsnip):
    """
    Iteratively removes peaks from data to find background for subtraction
    :param data: Smoothed double-log data
    :param snip_width: Snip width in points. Works best if all peaks have similar characteristic width
    :param nsnip: Number of iterations. 8 is a good starting point.
    :returns: snipped data (background)
    :rtype: 

    """
    if nsnip == 1:
        return snip1d(data, snip_width)
    else:
        return snip1d(itersnip(data, snip_width, nsnip-1), snip_width + nsnip)

def snip1d(data, snip_width):
    """
    One-pass peak removal
    :param data: 
    :param snip_width: 
    :returns: 
    :rtype: 

    """
    
    i = 0.5*snip_width
    w = np.zeros_like(data)
    z = np.copy(data)
    for p in range(snip_width, 0, -1):
        for i in range(p, len(data) - p):
            w[i] = min(z[i], 0.5*(z[i - p] + z[i + p]))
        for i in range(p, len(data) - p):
            z[i] = w[i]
    return z
