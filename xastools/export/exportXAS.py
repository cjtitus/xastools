from xastools.export.yamlExport import exportToYaml
from xastools.export.yamlExport import exportToSSRL

def inferColTypes(cols):
    motorNames = ['Seconds', 'ENERGY_ENC', 'MONO']
    sensorNames = ['TEMP']
    coltypes = []
    for c in cols:
        if c in motorNames:
            coltypes.append('motor')
        elif c in sensorNames:
            coltypes.append('sensor')
        else:
            coltypes.append('detector')
    return coltypes
    
def headerFromXAS(xas):
    scaninfokeys = ['motor', 'scan', 'date', 'sample', 'loadid', 'command']
    scaninfo = {k: getattr(xas, k, None) for k in scaninfokeys}
    scaninfo.update(xas.scaninfo)
    motors = xas.motors
    channelinfokeys = ['cols', 'offsets', 'weights'] #will require fixes for multiscans
    channelinfo = {k: getattr(xas, k, None) for k in channelinfokeys}

    header = {'scaninfo': scaninfo, 'motors': motors, 'channelinfo': channelinfo}
    return header

def dataFromXAS(xas, norm=None, offsetMono=False, **kwargs):
    # Will eventually deal with multiscans, etc
    if norm is not None:
        i0 = xas[norm]
        data = xas.data.copy()
        cols = np.array(xas.cols)
        if hasattr(xas, coltypes):
            coltypes = xas.coltypes
        else:
            coltypes = inferColTypes(cols)
        normidx = (np.array(coltypes) == 'detector')
        data[:, normidx, ...] = xas.getData(cols[normidx], offsetMono=offsetMono, return_x=False, individual=True)/i0[:, np.newaxis, ...]
    if len(data.shape) > 2:
        data = np.mean(data, axis=-1)
    return xas.data
    
def exportXASToYaml(xas, folder, namefmt="{sample}_{scan}.yaml", **kwargs):
    data = dataFromXAS(xas, **kwargs)
    header = headerFromXAS(xas)
    exportToYaml(folder, header, data, namefmt)

def exportXASToSSRL(xas, folder, namefmt="{sample}_{scan}.dat", **kwargs):
    data = dataFromXAS(xas, **kwargs)
    header = headerFromXAS(xas)
    exportToSSRL(folder, header, data, namefmt)
