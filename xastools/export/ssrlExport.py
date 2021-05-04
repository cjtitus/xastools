import numpy as np
from os.path import exists, join
from os import mkdir


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

