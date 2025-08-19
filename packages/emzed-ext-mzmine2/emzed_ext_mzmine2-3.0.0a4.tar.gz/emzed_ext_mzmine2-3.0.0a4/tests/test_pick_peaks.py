#! /usr/bin/env python
# Copyright © 2019 Uwe Schitt <uwe.schmitt@id.ethz.ch>

import pytest

from emzed import PeakMap
from emzed_ext_mzmine2 import (
    ADAPChromatogramBuilder,
    ADAPDetector,
    BaselinePeakDetector,
    IntensityWindowsSNParameters,
    MinimumSearchPeakDetector,
    NoiseAmplitudePeakDetector,
    RemoveShoulderPeaksParameters,
    SavitzkyGolayPeakDetector,
    WaveletCoefficientsSNParameters,
    pick_peaks,
)


@pytest.fixture
def pm(data_path):
    yield PeakMap.load(data_path("test_smallest.mzXML"))


def test_parameters(regtest):
    p = ADAPChromatogramBuilder()
    print(p.__doc__, file=regtest)

    p.mz_tolerance = (0.0, 5)
    p.minimum_scan_span = 3
    p.intensity_thresh2 = 3.0
    p.start_intensity = 3.0

    with pytest.raises(ValueError):
        p.mz_tolerance = 0

    with pytest.raises(ValueError):
        p.mz_tolerance = (0, 1, 2)

    with pytest.raises(ValueError):
        p.minimum_scan_span = 0

    with pytest.raises(ValueError):
        p.intensity_thresh2 = -1.0

    with pytest.raises(ValueError):
        p.start_intensity = -1.0

    with pytest.raises(AttributeError):
        p.abc = 3


@pytest.mark.parametrize(
    "peak_resolver",
    [
        BaselinePeakDetector(),
        NoiseAmplitudePeakDetector(),
        SavitzkyGolayPeakDetector(),
        MinimumSearchPeakDetector(),
        ADAPDetector(
            sn_estimators=WaveletCoefficientsSNParameters(),
            rt_for_cwt_scales_duration=(0.01, 0.1),
        ),
    ],
    ids=[
        "BaselinePeakDetector",
        "NoiseAmplitudePeakDetector",
        "SavitzkyGolayPeakDetector",
        "MinimumSearchPeakDetector",
        "ADAPDetector",
    ],
)
def test_pick_peaks(pm, regtest, peak_resolver):

    p = ADAPChromatogramBuilder()

    p.intensity_thresh2 = 3.0
    p.start_intensity = 3.0

    # 3. reorder columns like in emzed peak picker.

    print(peak_resolver, file=regtest)

    result = pick_peaks(pm, p, peak_resolver)

    chromatograms = result.filter(result.parent_id.is_none())
    picked_peaks = result.filter(result.parent_id.is_not_none())

    print(chromatograms, file=regtest)
    print(picked_peaks, file=regtest)


def test_pick_peaks_with_shoulder_peaks_removal(pm, regtest):

    p = ADAPChromatogramBuilder()

    p2 = RemoveShoulderPeaksParameters()

    p.mz_tolerance = (0.0, 5)
    p.minimum_scan_span = 3
    p.intensity_thresh2 = 3.0
    p.start_intensity = 3.0

    p2.resolution = 10_000
    p2.peak_model = "GAUSS"

    result = pick_peaks(pm, p, BaselinePeakDetector(peak_duration=(0.005, 10)), p2)

    result.print_(stream=regtest)


@pytest.mark.parametrize(
    "peak_resolver",
    [BaselinePeakDetector, NoiseAmplitudePeakDetector, SavitzkyGolayPeakDetector],
)
def test_peak_resolver(peak_resolver, regtest):

    p = peak_resolver()
    p._check_if_all_parameters_are_set()
    print(p, file=regtest)
    print(file=regtest)
    print(p.__doc__, file=regtest)
    print(file=regtest)
    print(p._to_dict(), file=regtest)


def test_mininum_search_peak_detector(regtest):
    p = MinimumSearchPeakDetector()

    p.search_rt_range = 10
    p.min_relative_height = 0
    p.min_absolute_height = 0
    p.min_ratio = 0.1
    p.chromatographic_threshold_level = 0.1
    p._check_if_all_parameters_are_set()

    print(p, file=regtest)
    print(file=regtest)
    print(p.__doc__, file=regtest)
    print(file=regtest)
    print(p._to_dict(), file=regtest)


def test_adap_detector(regtest):
    p = ADAPDetector()

    with pytest.raises(ValueError):
        p._check_if_all_parameters_are_set()

    for estimator in (
        WaveletCoefficientsSNParameters(),
        IntensityWindowsSNParameters(),
    ):
        p.sn_estimators = estimator

        p._check_if_all_parameters_are_set()
        print(p, file=regtest)
        print(file=regtest)
        print(p.__doc__, file=regtest)
        print(file=regtest)
        print(p._to_dict(), file=regtest)
        print(file=regtest)
