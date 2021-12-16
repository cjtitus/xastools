import pytest
from xastools.xas import XAS
from xastools.io import loadOne

def test_xas_equality():
    filename = "canonical.yaml"
    xas = loadOne(filename)
    xas2 = loadOne(filename)
    assert xas == xas2
