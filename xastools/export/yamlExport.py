import yaml
from os.path import join
import numpy as np


def writeHeader(filename, header):
    def ndrep(dumper, data):
        return dumper.represent_data([float(d) for d in data])
    yaml.add_representer(np.ndarray, ndrep)
    
    with open(filename, 'w') as f:
        yaml.dump(header, f, explicit_end=True)

def writeData(filename, scanData):
    datafmt = ' %14.3f'
    with open(filename, 'ba') as f:
        np.savetxt(f, scanData.T, fmt=datafmt)

    
def exportToYaml(folder, header, data, namefmt="{sample}_{scan}.yaml"):
    """Exports header, data to a YAML-based format

    :param folder: target folder for export
    :param header: Header dictionary consisting of 'scaninfo', 'motors', 'channelinfo' subdictionaries
    :param data: numpy array of data
    :param namefmt: format string consisting of keys in scaninfo dictionary
    :returns: 
    :rtype: 

    """
    
    filename = join(folder, namefmt.format(**header['scaninfo']))
    writeHeader(filename, header)
    writeData(filename, data)

def loadFromYaml(filename):
    with open(filename, 'r') as f:
        document = f.readlines()
    yamlEnd = document.index("...\n") + 1
    yamlStr = "".join(document[:yamlEnd])
    header = yaml.load(yamlStr)
    data = np.loadtxt(document[yamlEnd:]).T
    return header, data
