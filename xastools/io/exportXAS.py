import numpy as np
from .yamlExport import exportToYaml
from .ssrlExport import exportToSSRL
from .athenaExport import exportToAthena
from ..xas import inferColTypes


def headerFromXAS(xas, data=None):
    scaninfokeys = ["motor", "date", "sample", "loadid", "command"]
    scaninfo = {k: getattr(xas, k, None) for k in scaninfokeys}
    scan = sorted(xas.data.scan.values.tolist())
    if len(scan) == 1:
        scan = scan[0]
    scaninfo["scan"] = scan
    scaninfo.update(getattr(xas, "scaninfo", {}))
    motors = getattr(xas, "motors", {})
    channelinfokeys = ["cols"]  # will require fixes for multiscans
    channelinfo = {k: xas.channelinfo.get(k, None) for k in channelinfokeys}
    if data is not None:
        w = data.weights
        o = data.offsets
    else:
        w = xas.data.weights.isel(scan=0)
        o = xas.data.offsets.isel(scan=0)
    weights = {
        str(c): float(v) for c, v in zip(w.ch.values, w.values) if not np.isnan(v)
    }
    offsets = {
        str(c): float(v) for c, v in zip(o.ch.values, o.values) if not np.isnan(v)
    }
    channelinfo["weights"] = weights
    channelinfo["offsets"] = offsets

    header = {"scaninfo": scaninfo, "motors": motors, "channelinfo": channelinfo}
    return header


def dataFromXAS(xas, norm=None, offsetMono=False, exclude=[], **kwargs):
    # Will eventually deal with multiscans, etc
    scans = xas.getIncludedScans(exclude)
    data = xas.data.sel(scan=scans).copy(deep=True)
    cols = np.array(xas.channelinfo["cols"])
    if hasattr(xas.channelinfo, "coltypes"):
        coltypes = xas.channelinfo["coltypes"]
    else:
        coltypes = inferColTypes(cols)
    coltypes = np.array(coltypes)
    detectors = cols[coltypes == "detector"]
    rawdata = xas.getData(
        detectors,
        offsetMono=offsetMono,
        divisor=norm,
        return_x=False,
        individual=True,
        exclude=exclude,
        **kwargs
    )

    data.data.loc[{"ch": detectors}] = rawdata
    data = data.mean(dim="scan")
    return data


def getDataAndHeader(xas, **kwargs):
    data = dataFromXAS(xas, **kwargs)
    header = headerFromXAS(xas, data)
    d = data.data.sel(ch=header["channelinfo"]["cols"]).values
    return d, header


def exportXASToYaml(
    xas, folder, namefmt="{sample}_{scan}.yaml", increment=True, **kwargs
):
    data, header = getDataAndHeader(xas, **kwargs)
    exportToYaml(folder, data, header, namefmt, increment=increment)


def exportXASToSSRL(
    xas, folder, namefmt="{sample}_{scan}.dat", increment=True, **kwargs
):
    data, header = getDataAndHeader(xas, **kwargs)
    exportToSSRL(folder, data, header, namefmt, increment=increment)


def exportXASToAthena(
    xas, folder, namefmt="{sample}_{scan}.dat", increment=True, **kwargs
):
    data, header = getDataAndHeader(xas, **kwargs)
    exportToAthena(folder, data, header, namefmt, increment=increment)
