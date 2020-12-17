import unittest
from xastools import xy as xas
import os.path as path
from os import remove
import numpy as np

class TestXASSetup(unittest.TestCase):
    def test_data_and_cols_unequal_length_throws_exception(self):
        datax = np.linspace(0, 6, 100)
        datay = np.sin(datax)
        xcols = ['x']
        ycols = ['y', 'z']
        self.header = {'xcols': xcols, 'ycols': ycols}
        self.datax = datax
        self.datay = datay
        self.data = np.vstack([datax, datay])

        with self.assertRaises(ValueError):
            s = xas.XY(self.data, self.header)

class TestXAS(unittest.TestCase):
    def setUp(self):
        datax = np.linspace(0, 6, 100)
        datay = np.sin(datax)
        xcols = ['x']
        ycols = ['y']
        self.header = {'xcols': xcols, 'ycols': ycols}
        self.datax = datax
        self.datay = datay
        self.data = np.vstack([datax, datay])
        self.spectra = xas.XY(self.data, self.header)
        
    def test_get_column(self):
        x = self.spectra.getxData('x')
        self.assertTrue(np.all(x == self.datax))
        y = self.spectra.getyData('y')
        self.assertTrue(np.all(y == self.datay))

    def test_copy_points_to_different_object(self):
        snew = self.spectra.copy()
        self.assertFalse(snew is self.spectra)

    def test_copy_data_is_different_reference(self):
        immutable_types = [int, float, complex, tuple, str, frozenset, bool]
        snew = self.spectra.copy()
        for k in vars(snew):
            new_attr = getattr(snew, k)
            old_attr = getattr(self.spectra, k)
            if type(new_attr) in immutable_types:
                continue
            else:
                self.assertNotEqual(id(new_attr), id(old_attr), msg='Testing attr %s'%k)

    def test_copy_data_is_equal(self):
        snew = self.spectra.copy()
        new_attr_list = vars(snew)
        old_attr_list = vars(self.spectra)
        self.assertEqual(set(new_attr_list), set(old_attr_list))
        for k in vars(snew):
            new_attr = getattr(snew, k)
            old_attr = getattr(self.spectra, k)
            self.assertTrue(np.all(new_attr == old_attr))

class TestXASSaveLoad(unittest.TestCase):
    def setUp(self):
        datax = np.linspace(0, 6, 100)
        datay = np.sin(datax)
        xcols = ['x']
        ycols = ['y']
        self.header = {'xcols': xcols, 'ycols': ycols}
        self.datax = datax
        self.datay = datay
        self.data = np.vstack([datax, datay])
        self.spectra = xas.XY(self.data, self.header)
        self.filename = 'test_xas.xy'
        
        self.data2 = np.vstack([datax, datay, datay])
        self.header2 = {'xcols': xcols, 'ycols': ['y', 'z']}
        self.spectra2 = xas.XY(self.data2, self.header2)
        
        if path.exists(self.filename):
            remove(self.filename)

    def tearDown(self):
        if path.exists(self.filename):
            remove(self.filename)
        
    def test_save_xas_creates_file(self):
        self.spectra.save(self.filename)
        self.assertTrue(path.exists(self.filename))

    def test_load_xas_fails_on_missing_file(self):
        self.assertRaises(FileNotFoundError, lambda x: xas.load(x), self.filename)

    def test_load_xas_fails_on_empty_file(self):
        with open(self.filename, 'w') as f:
            f.write("")
        self.assertRaises(ValueError, lambda x: xas.load(x), self.filename)

    def test_load_xas_returns_same_xas(self):
        self.spectra2.save(self.filename)
        s = xas.load(self.filename)
        self.assertTrue(isinstance(s, xas.XY))
        for k in vars(self.spectra2):
            new_attr = getattr(s, k)
            old_attr = getattr(self.spectra2, k)
            self.assertTrue(np.all(new_attr == old_attr))

    def test_load_basic_np_file(self):
        x = self.spectra.getxData()
        y = self.spectra.getyData()
        np.savetxt(self.filename, np.vstack([x, y]).T)
        s = xas.load(self.filename)
        for k in vars(self.spectra):
            new_attr = getattr(s, k)
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
        header = {'xcols': xcols, 'ycols': ycols}
        self.data = {'x': datax, 'y': datay, 'z': dataz}
        self.spectra = xas.XY(data, header)
        self.double = self.spectra + self.spectra
        self.short = xas.XY(np.vstack([datax, datay]), {'xcols': xcols, 'ycols':['y']})
        self.different = xas.XY(np.vstack([datax, datay, dataz]), {'xcols': xcols, 'ycols': ['t', 'z']})
        
    def test_add_two_spectra_adds_data(self):
        s = self.spectra + self.spectra
        for c in s.getyCols():
            self.assertTrue(np.all(s.getyData(c) == (self.data[c] + self.data[c])))

    def test_added_spectrum_is_independent(self):
        immutable_types = [int, float, complex, tuple, str, frozenset, bool]
        for k in vars(self.double):
            new_attr = getattr(self.double, k)
            old_attr = getattr(self.spectra, k)
            if type(new_attr) in immutable_types:
                continue
            else:
                self.assertNotEqual(id(new_attr), id(old_attr), msg='Testing attr %s'%k)
        
    def test_raise_value_error_if_add_different_column_lengths(self):
        self.assertRaises(ValueError, lambda x, y: x + y, self.short, self.spectra)

    def test_raise_value_error_if_add_different_column_names(self):
        self.assertRaises(ValueError, lambda x, y: x + y, self.different, self.spectra)

    def test_raise_value_error_if_add_different_row_lengths(self):
        truncated = xas.XY(np.vstack([self.data['x'][:-10], self.data['y'][:-10], self.data['z'][:-10]]), {'xcols': ['x'], 'ycols': ['y', 'z']})
        self.assertRaises(ValueError, lambda x, y: x + y, self.spectra, truncated)
        
    def test_add_two_spectra_does_not_add_x(self):
        xcols1 = self.spectra.getxData()
        xcols2 = self.double.getxData()
        self.assertTrue(np.all(xcols1 == xcols2))
        
        
