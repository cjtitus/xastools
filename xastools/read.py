import numpy as np
from copy import copy
from six import string_types
import matplotlib.pyplot as plt
import datetime
        
def readSSRL(filename):
    """
    :param filename: SSRL .dat file to read in
    returns data, header
    """
    with open(filename, 'r') as f:
        f.readline()
        dateline = f.readline()
        fmtline = f.readline().split()
        npts = int(fmtline[1])
        ncols = int(fmtline[3])
        for n in range(4): f.readline()
        sampleline = f.readline().split()
        sample = sampleline[1]
        loadid = sampleline[3]
        cmdline = f.readline().rstrip('\n')
        slitline = f.readline().rstrip('\n')
        manipline = f.readline().rstrip('\n')
        scanline = f.readline().split()
        try:
            scan = scanline[1]
        except:
            scan = None
        for n in range(2): f.readline()
        f.readline()
        weightline = f.readline().split()
        f.readline()
        offsetline = f.readline().split()
        f.readline()
        cols = [f.readline().rstrip('\n') for n in range(ncols)]
    data = np.loadtxt(filename, skiprows=(20+ncols))
    header = {}
    header['sample'] = sample
    header['loadid'] = loadid
    header['cmd'] = cmdline
    header['cols'] = cols
    header['scan'] = scan
    header['weights'] = weightline
    header['offsets'] = offsetline
    header['slits'] = map(lambda x: float(x), slitline.split()[1:])
    return data, header

def writeSSRL(filename, cols, data, date=None, sample='sample', loadid='0', cmd='cmd', scan=None, slits=None, manip=None, weights=None, offsets=None, c1="", c2=""):
    datafmt = ' %14.6g'
    scandata = {}
    for n, c in enumerate(cols):
        d = data[:, n]
        scandata[c] = list(map(lambda x: datafmt%x, d))
    
    ncols = len(cols)
    npts = data.shape[0]
    if date is None:
        date = datetime.datetime.today().strftime("%a %b %d %H:%M:%S %Y")
    if slits is None:
        slits = (0, 0)
    if manip is None:
        manip = (0, 0, 0, 0)
    if scan is None:
        scan = 0
    if weights is None:
        header.append("".join([' %7.3g'%1]*ncols))
    header = []
    header.append('SSRL                                  ')
    header.append(date)
    header.append('PTS:%11d COLS: %11d'%(npts, ncols))
    header.append('scaler_file')
    header.append('region_file')
    header.append('')
    header.append('4 2000 5 RST 2 1')
    header.append('Sample: ' + sample + '  loadid: ' + loadid)
    header.append('Command: ' + cmd)
    header.append('Slits: %.2f %.2f'%tuple(slits))
    header.append('Manipulator Position (XYZR): %.2f %.2f %.2f %.2f'%tuple(manip))
    header.append('Scan: %d'%scan)
    header.append(c1)
    header.append(c2)
    header.append("Weights:")
    if weights is None:
        header.append("".join([' %7.3g'%1]*ncols))
    else:
        header.append("".join([' %7.3g'%weight for weight in weights]))
    header.append("Offsets:")
    if offsets is None:
        header.append("".join([' %7.3g'%0]*ncols))
    else:
        header.append("".join([' %7.3g'%offset for offset in offsets]))
    header.append("Data:")
    for c in cols:
        header.append(c)
    header.append("")
    with open(filename, 'w') as f:
        f.writelines(map(lambda x: x + '\n', header))
        writeData(f, scandata, cols, sep="")

def writeData(f2, scanData, newKeys, sep=" "):
    d = np.vstack([scanData[k] for k in newKeys])
    for n in range(d.shape[1]):
        f2.write(sep.join(d[:, n]) + '\n')

