import unittest
from xastools import xas_refactor as xas
import numpy as np

class TestXASSetup(unittest.TestCase):
    def test_data_and_cols_unequal_length_throws_exception(self):
        datax = np.linspace(0, 6, 100)
        datay = np.sin(datax)
        xcols = ['x']
        ycols = ['y', 'z']
        self.assertRaises(ValueError, xas.XAS, datax, datay, xcols, ycols)

class TestXAS(unittest.TestCase):
    def setUp(self):
        datax = np.linspace(0, 6, 100)
        datay = np.sin(datax)
        xcols = ['x']
        ycols = ['y']
        self.datax = datax
        self.datay = datay
        self.spectra = xas.XAS(datax, datay, xcols, ycols)
        
    def test_get_column(self):
        x = self.spectra.getxData('x')
        self.assertTrue(np.all(x == self.datax))
        y = self.spectra.getyData('y')
        self.assertTrue(np.all(y == self.datay))

    def test_copy_points_to_different_object(self):
        snew = self.spectra.copy()
        self.assertFalse(snew is self.spectra)

    def test_copy_data_is_different_reference(self):
        snew = self.spectra.copy()
        for k in vars(snew):
            new_attr = getattr(snew, k)
            old_attr = getattr(self.spectra, k)
            self.assertFalse(id(new_attr) == id(old_attr))

    def test_copy_data_is_equal(self):
        snew = self.spectra.copy()
        for k in vars(snew):
            new_attr = getattr(snew, k)
            old_attr = getattr(self.spectra, k)
            self.assertTrue(np.all(new_attr == old_attr))

class TestXASAddition(unittest.TestCase):
    def setUp(self):
        datax = np.linspace(0, 6, 100)
        datay = np.sin(datax)
        dataz = np.cos(datax)
        data = np.vstack([datax, datay, dataz])
        xcols = ['x']
        ycols = ['y', 'z']
        self.data = {'x': datax, 'y': datay, 'z': dataz}
        self.spectra = xas.XAS(datax, np.vstack([datay, dataz]), xcols, ycols)
        self.double = self.spectra + self.spectra
        self.short = xas.XAS(datax, datay, xcols, ['y'])
        self.different = xas.XAS(datax, np.vstack([datay, dataz]), xcols, ['t', 'z'])
        
    def test_add_two_spectra_adds_data(self):
        s = self.spectra + self.spectra
        for c in s.getyCols():
            self.assertTrue(np.all(s.getyData(c) == (self.data[c] + self.data[c])))

    def test_added_spectrum_is_independent(self):
        for k in vars(self.double):
            new_attr = getattr(self.double, k)
            old_attr = getattr(self.spectra, k)
            self.assertFalse(id(new_attr) == id(old_attr))
        
    def test_raise_value_error_if_add_different_column_lengths(self):
        self.assertRaises(ValueError, lambda x, y: x + y, self.short, self.spectra)

    def test_raise_value_error_if_add_different_column_names(self):
        self.assertRaises(ValueError, lambda x, y: x + y, self.different, self.spectra)

    def test_raise_value_error_if_add_different_row_lengths(self):
        truncated = xas.XAS(self.data['x'][:-10], np.vstack([self.data['y'][:-10], self.data['z'][:-10]]), ['x'], ['y', 'z'])
        self.assertRaises(ValueError, lambda x, y: x + y, self.spectra, truncated)
        
    def test_add_two_spectra_does_not_add_x(self):
        xcols1 = self.spectra.getxData()
        xcols2 = self.double.getxData()
        self.assertTrue(np.all(xcols1 == xcols2))
        
        
