#! /usr/bin/env python
# Copyright © 2019 Uwe Schitt <uwe.schmitt@id.ethz.ch>

from collections import Counter

from emzed import PeakMap
from emzed_ext_mzmine2 import RemoveShoulderPeaksParameters, remove_shoulder_peaks


def test_remove_shoulder_peaks(data_path, regtest):

    parameters = RemoveShoulderPeaksParameters()
    print(parameters, file=regtest)

    pm = PeakMap.load(data_path("test_smallest.mzXML"))
    pm_back = remove_shoulder_peaks(pm, parameters)

    assert pm != pm_back
    assert pm_back.spectra[0].mzs.shape == (340,)
    assert pm_back.spectra[1].mzs.shape == (361,)

    assert all(s.rt == s_back.rt for (s, s_back) in zip(pm.spectra, pm_back.spectra))


def test_remove_shoulder_peaks_ms2(data_path):

    parameters = RemoveShoulderPeaksParameters()
    parameters.resolution = 10000.0
    parameters.peak_model = "GAUSS"

    pm = PeakMap.load(data_path("ms2_peaks_only.mzXML"))
    pm_back = remove_shoulder_peaks(pm, parameters)

    assert pm == pm_back


def test_remove_shoulder_peaks_ms1_ms2_mixed(data_path):

    parameters = RemoveShoulderPeaksParameters()
    parameters.resolution = 10000.0
    parameters.peak_model = "GAUSS"

    pm = PeakMap.load(data_path("ms1_and_ms2_mixed.mzML"))
    pm_back = remove_shoulder_peaks(pm, parameters)

    assert len(pm) == len(pm_back)

    assert Counter(s.ms_level for s in pm) == Counter(s.ms_level for s in pm_back)
