from copy import copy
import numpy as np

class XAS:
    def __init__(self, xdata, ydata, xcols, ycols):
        self.xdata = np.atleast_2d(xdata)
        self.ydata = np.atleast_2d(ydata)
        self.xcols = xcols
        self.ycols = ycols
        if self.xdata.shape[0] != len(self.xcols):
            raise ValueError
        if self.ydata.shape[0] != len(self.ycols):
            raise ValueError
        
    def getxData(self, xcol=None):
        if xcol is None:
            return self.xdata
        else:
            idx = self.xcols.index(xcol)
            return self.xdata[idx, :]
    
    def getyData(self, ycol=None):
        if ycol is None:
            return self.ydata
        else:
            idx = self.ycols.index(ycol)
            return self.ydata[idx, :]

    def getxCols(self):
        return self.xcols

    def getyCols(self):
        return self.ycols

    def copy(self):
        xcols = copy(self.xcols)
        ycols = copy(self.ycols)
        xdata = self.xdata.copy()
        ydata = self.ydata.copy()
        return XAS(xdata, ydata, xcols, ycols)

    def __add__(self, y):
        if self.getyCols() != y.getyCols():
            raise ValueError
        newXAS = self.copy()
        data = self.ydata + y.ydata
        newXAS.ydata = data
        return newXAS
    
