import xarray as xr
import numpy as np


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


def convertDataHeader(data, header):
    scan = header['scaninfo'].pop('scan', None)
    cols = header['channelinfo']['cols']
    offsets = header['channelinfo'].pop('offsets', {})
    weights = header['channelinfo'].pop('weights', {})
    if "coltypes" not in header['channelinfo']:
        coltypes = np.array(inferColTypes(cols))
        header['channelinfo']['coltypes'] = coltypes
    x = xr.DataArray(data, dims=['index', 'ch'], coords={'ch': cols})
    offset_cols = list(offsets.keys())
    offset_data = np.array([offsets[k] for k in offset_cols])
    o = xr.DataArray(offset_data, dims=["ch"], coords=[offset_cols])
    weight_cols = list(weights.keys())
    weight_data = np.array([weights[k] for k in weight_cols])
    w = xr.DataArray(weight_data, dims=["ch"], coords=[weight_cols])
    d = xr.Dataset({"data": x, "offsets": o, "weights": w})

    if isinstance(scan, int):
        d = d.expand_dims({"scan": [scan]})
    else:
        d = d.expand_dims({"scan": [scan[0]]})
    return d, header
