import numpy as np
from xastools.export.exportTools import inferColTypes

def parseChannelLine(line, ncols, default, name='Channel Line'):
    values = line.split()
    
    if len(values) != ncols:
        print("{} has len {}, expected {}".format(name, len(values), ncols))
        print(values)
        values = np.array([default]*ncols)
    else:
        try:
            values = np.array(values, dtype=float)
        except:
            values = np.array([default]*ncols)
    return values
    
def parseWeights(line, ncols):
    """

    :param line: Either a weight
    :returns: 
    :rtype: 

    """
    weights = parseChannelLine(line, ncols, 1.0, name='Weights')
    return weights

def parseOffsets(line, ncols):
    """

    :param line: Either a weight
    :returns: 
    :rtype: 

    """
    offsets = parseChannelLine(line, ncols, 0.0, name='Offsets')
    return offsets

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
        weightline = f.readline()
        f.readline()
        offsetline = f.readline()
        f.readline()
        cols = [f.readline().rstrip('\n') for n in range(ncols)]
    data = np.loadtxt(filename, skiprows=(20+ncols)).T
    header = {}
    scaninfo = {}
    scaninfo['date'] = dateline.rstrip('\n')
    scaninfo['sample'] = sample
    scaninfo['loadid'] = loadid
    scaninfo['command'] = cmdline[9:]
    scaninfo['scan'] = scan

    channelinfo = {}
    channelinfo['cols'] = cols
    channelinfo['coltypes'] = inferColTypes(cols)
    channelinfo['weights'] = parseWeights(weightline, ncols)
    channelinfo['offsets'] = parseOffsets(offsetline, ncols)
    motors = {}
    try:
        motors['entnslt'] = float(slitline.split()[1])
        motors['exslit'] = float(slitline.split()[2])
    except:
        pass
    try:
        manip_pos = manipline.split(':')[-1]
        x, y, z, r = manip_pos.split()
        motors['samplex'] = float(x)
        motors['sampley'] = float(y)
        motors['samplez'] = float(z)
        motors['sampler'] = float(r)
    except:
        pass
    header['scaninfo'] = scaninfo
    header['motors'] = motors
    header['channelinfo'] = channelinfo

    return data, header
