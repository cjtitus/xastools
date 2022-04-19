from functools import reduce
from ..xas import XAS
from .yamlExport import loadFromYaml
from .ssrlExport import loadFromSSRL
from .exportTools import convertDataHeader


def loadOne(filename):
    ext = filename.split('.')[-1]
    if ext == 'yaml':
        data, header = loadFromYaml(filename)
    elif ext == "dat":
        data, header = loadFromSSRL(filename)
    else:
        raise ValueError("File extension not recognized")
    return XAS.from_data_header(data, header)


def loadMany(filenames):
    spectra = []
    for f in filenames:
        spectra.append(loadOne(f))
    return spectra


def loadCombined(filenames):
    spectra = loadMany(filenames)
    #spectra.sort(key=lambda x: x.scans[0])
    return reduce(lambda x, y: x + y, spectra)


def load(filenames):
    """
    Takes one or more filenames and returns a single combined XAS object
    """
    if isinstance(filenames, str):
        return loadOne(filenames)
    else:
        return loadCombined(filenames)
