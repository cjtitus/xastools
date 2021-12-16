import pytest
import os
from xastools.io import loadOne, exportXASToYaml, exportXASToSSRL


@pytest.fixture
def xas():
    filename = "canonical.yaml"
    spectrum = loadOne(filename)
    yield spectrum


def test_yaml_roundtrip():
    filename1 = "canonical.yaml"
    xas = loadOne(filename1)
    filename2 = "roundtrip.yaml"
    exportXASToYaml(xas, '.', namefmt=filename2)
    xas2 = loadOne(filename2)
    assert xas == xas2
    os.remove(filename2)


def test_ssrl_roundtrip(xas):
    filename = "roundtrip.dat"
    exportXASToSSRL(xas, '.', namefmt=filename)
    xas2 = loadOne(filename)
    assert xas == xas2
    os.remove(filename)
