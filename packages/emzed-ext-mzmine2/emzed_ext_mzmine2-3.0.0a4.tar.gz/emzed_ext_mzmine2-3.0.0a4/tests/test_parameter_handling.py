#! /usr/bin/env python
# Copyright © 2019 Uwe Schitt <uwe.schmitt@id.ethz.ch>

# from emzed.ext.mzmine2.classes import MzMine2Class

import pickle

import dill
import pytest

from emzed_ext_mzmine2._parameters import ParameterBaseMeta


class XTestParameters(metaclass=ParameterBaseMeta):
    _java_class = "ShoulderPeaksFilterParameters"
    _fields = ["resolution", "peakModel", "autoRemove"]

    def _check_resolution(self, value):
        return value > 0, "value must be positive"


def test_param_conversion(regtest):

    py_obj = XTestParameters()
    py_obj.resolution = 123
    py_obj.auto_remove = True
    py_obj.peak_model = "GAUSS"

    assert py_obj.resolution == 123.0
    assert py_obj.auto_remove is True
    assert py_obj.peak_model == "GAUSS"

    print(py_obj.__doc__, file=regtest)


def test_param_error_handling(regtest):
    py_obj = XTestParameters()
    with pytest.raises(ValueError) as e:
        py_obj.resolution = "1"

    print(e.value, file=regtest)

    with pytest.raises(ValueError) as e:
        py_obj.resolution = -1.0

    print(e.value, file=regtest)

    with pytest.raises(ValueError) as e:
        py_obj.auto_remove = 7

    print(e.value, file=regtest)

    with pytest.raises(ValueError) as e:
        py_obj.peak_model = "BLAFASL"

    print(e.value, file=regtest)

    with pytest.raises(ValueError) as e:
        py_obj.peak_model = 7

    print(e.value, file=regtest)


def test_param_str_conversion(regtest):
    py_obj = XTestParameters()
    print(py_obj, file=regtest)


def test_param_pickling():

    p = XTestParameters()
    p_back = pickle.loads(pickle.dumps(p))
    assert p.resolution == p_back.resolution
    assert p.peak_model == p_back.peak_model
    assert p.auto_remove == p_back.auto_remove

    p_back = dill.loads(dill.dumps(p))
    assert p.resolution == p_back.resolution
    assert p.peak_model == p_back.peak_model
    assert p.auto_remove == p_back.auto_remove
