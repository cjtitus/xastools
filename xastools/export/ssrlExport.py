import numpy as np
from os.path import exists, join
from os import mkdir
from xastools.export.exportTools import inferColTypes

def exportToSSRL(folder, header, data, namefmt="{sample}_{scan}.dat", c1="", c2="", headerUpdates={}):
    """Exports to Graham's ASCII SSRL data format

    :param folder: Export folder (filename will be auto-generated)
    :param header: Dictionary with 'scaninfo', 'motors', 'channelinfo' sub-dictionaries
    :param data: Numpy array with data
    :param namefmt: Python format string that will be filled with info from 'scaninfo' dictionary
    :param c1: Comment string 1
    :param c2: Comment string 2
    :param headerUpdates: Manual updates for header dictionary (helpful to fill missing info)
    :returns: 
    :rtype: 

    """
    
    filename = join(folder, namefmt.format(**header['scaninfo']))


    metadata = {}
    metadata.update(header['scaninfo'])
    metadata.update(headerUpdates)
    motors = header['motors']
    channelinfo = header['channelinfo']
    cols = channelinfo.get('cols')
    weights = channelinfo.get('weights', None)
    offsets = channelinfo.get('offsets', None)
    weightStr = makeWeightStr(weights, cols)
    offsetStr = makeOffsetStr(offsets, cols)
    colStr = "\n".join(cols)

    metadata['npts'] = data.shape[1]
    metadata['ncols'] = data.shape[0]
    metadata['cols'] = colStr
    metadata['weights'] = weightStr
    metadata['offsets'] = offsetStr
    metadata['c1'] = c1
    metadata['c2'] = c2
    
    headerstring = '''SSRL                                  
{date}
PTS:{npts:11d} COLS: {ncols:11d}
scaler_file
region_file

4 2000 5 RST 2 1
Sample: {sample}   loadid: {loadid}
Command: {command}
Slits: {entnslt:.2f} {exslit:.2f}
Maniplator Position (XYZ): {samplex:.2f} {sampley:.2f} {samplez:.2f} {sampler:.2f}
Scan: {scan}
{c1}
{c2}
Weights:
{weights}
Offsets:
{offsets}
Data:
{cols}

'''.format(**metadata, **motors)

    with open(filename, 'w') as f:
        f.write(headerstring)
        np.savetxt(f, data.T, fmt=' %14.3f')

def makeWeightStr(weights, cols):
    if weights is not None:
        weightStr = "".join([' %7.3f'%w for w in weights])
    else:
        weightStr = "".join([' %7.3f'%1]*len(cols))
    return weightStr

def makeOffsetStr(offsets, cols):
    if offsets is not None:
        offsetStr = "".join([' %7.3f'%o for o in offsets])
    else:
        offsetStr = "".join([' %7.3f'%0]*len(cols))
    return offsetStr

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

def loadFromSSRL(filename):
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

    return header, data
