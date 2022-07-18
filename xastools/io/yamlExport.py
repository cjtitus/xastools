import yaml
from os.path import join
import numpy as np


def writeHeader(filename, header):
    def ndrep(dumper, data):
        return dumper.represent_data([float(d) for d in data])
    yaml.add_representer(np.ndarray, ndrep)

    def nintrep(dumper, data):
        return dumper.represent_data(int(data))

    yaml.add_representer(np.integer, nintrep)

    with open(filename, 'w') as f:
        yaml.dump(header, f, explicit_end=True)


def writeData(filename, scanData):
    datafmt = ' %8g'
    with open(filename, 'ba') as f:
        np.savetxt(f, scanData, fmt=datafmt)


def exportToYaml(folder, data, header, namefmt="{sample}_{scan}.yaml", verbose=True):
    """Exports header, data to a YAML-based format

    :param folder: target folder for export
    :param data: numpy array of data
    :param header: Header dictionary consisting of 'scaninfo', 'motors', 'channelinfo' subdictionaries
    :param namefmt: format string consisting of keys in scaninfo dictionary
    :returns: 
    :rtype: 

    """

    filename = join(folder, namefmt.format(**header['scaninfo']))
    if verbose:
        print(f"Exporting to {filename}")
    writeHeader(filename, header)
    writeData(filename, data)


def loadFromYaml(filename):
    with open(filename, 'r') as f:
        document = f.readlines()
    yamlEnd = document.index("...\n") + 1
    yamlStr = "".join(document[:yamlEnd])
    header = yaml.load(yamlStr)
    data = np.loadtxt(document[yamlEnd:])
    return data, header
