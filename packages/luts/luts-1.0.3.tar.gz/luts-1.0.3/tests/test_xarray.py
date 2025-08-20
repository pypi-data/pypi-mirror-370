#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Test conversion to/from xarray objects
'''

from tests.test_luts import create_lut, create_mlut
from luts import MLUT
import numpy as np
import xarray as xr
from luts import from_xarray

def test_mlut_to_xrdataset():
    m = create_mlut()

    ds = m.to_xarray()
    print(ds)


def test_lut_to_xrdataarray_1():
    l = create_lut()
    print(l.to_xarray())


def test_lut_to_xrdataarray_2():
    m = create_mlut()
    print(m['data3'].to_xarray())


def test_lut_to_xrdataarray_3():
    """ test with deduplicate """
    m = MLUT()
    m.add_axis('a', np.linspace(100, 150, 5))
    m.add_dataset('data', np.linspace(1000, 1100, 5*4*5).reshape((5, 4, 5)), ['a', 'b', 'a'])

    print(m['data'].to_xarray(deduplicate={'a': ['a0', 'a1']}))


def test_xrdataset_to_mlut():
    ds = xr.tutorial.open_dataset('air_temperature')
    m = from_xarray(ds)
    m.describe(show_attrs=True)

def test_xrdataarray_to_lut():
    air = xr.tutorial.open_dataset('air_temperature').air

    l = from_xarray(air)
    l.describe(show_attrs=True)
