#! /usr/bin/env python
# Copyright 2020 Uwe Schmitt <uwe.schmitt@id.ethz.ch>

from ._parameters import ParameterBaseMeta


class PeakResolver:
    pass


# we want to check for sublcassing a general PeakResolver class (within isinstance) and
# at the same time we want the convenience from using the ParameterBaseMeta meta class.
# the appraoch
#
#    class BaselinePeakDetector(PeakResolver, metaclass=ParameterBaseMeta):
#        ...
#
# raises an TypeError with message
#
#     metaclass conflict: the metaclass of a derived class must be a (non-strict)
#     subclass of the metaclasses of all its bases
#
# so instead we first create a proxy class _BaselinePeakDetector which utilizes
# the meta class and eventually create BaselinePeakDetector with the two base
# classes PeakResolver and _BaselinePeakDetector.
#
# this was just an example we use this strategy for all peak resolvers below.


class _BaselinePeakDetector(metaclass=ParameterBaseMeta):

    _java_class = "BaselinePeakDetectorParameters"

    _fields = ["MIN_PEAK_HEIGHT", "PEAK_DURATION", "BASELINE_LEVEL"]
    _time_in_minutes = ("PEAK_DURATION",)
    _defaults = {
        "min_peak_height": 0.0,
        "baseline_level": 0.0,
        "peak_duration": (0.001, 5),  # minutes!
    }


class BaselinePeakDetector(PeakResolver, _BaselinePeakDetector):
    __doc__ = _BaselinePeakDetector.__doc__

    def _check_peak_duration(self, value):
        duration_min, duration_max = value
        if duration_min <= 0:
            return False, "first entry of peak_duration must be larger than 0"
        if duration_max <= duration_min:
            return (
                False,
                "second entry of peak_duration must be larger than first entry",
            )
        return True, ""


class _NoiseAmplitudePeakDetector(metaclass=ParameterBaseMeta):

    _java_class = "NoiseAmplitudePeakDetectorParameters"

    _fields = ["MIN_PEAK_HEIGHT", "PEAK_DURATION", "NOISE_AMPLITUDE"]
    _time_in_minutes = ("PEAK_DURATION",)

    _defaults = {"min_peak_height": 0.0, "noise_amplitude": 0.0}


class NoiseAmplitudePeakDetector(PeakResolver, _NoiseAmplitudePeakDetector):
    __doc__ = _NoiseAmplitudePeakDetector.__doc__


class _SavitzkyGolayPeakDetector(metaclass=ParameterBaseMeta):

    _java_class = "SavitzkyGolayPeakDetectorParameters"

    _fields = ["MIN_PEAK_HEIGHT", "PEAK_DURATION", "DERIVATIVE_THRESHOLD_LEVEL"]
    _time_in_minutes = ("PEAK_DURATION",)

    _defaults = {
        "min_peak_height": 0.0,
        "derivative_threshold_level": 0.0,
        "peak_duration": (0, 5),
    }


class SavitzkyGolayPeakDetector(PeakResolver, _SavitzkyGolayPeakDetector):
    __doc__ = _SavitzkyGolayPeakDetector.__doc__


class _MinimumSearchPeakDetector(metaclass=ParameterBaseMeta):

    _java_class = "MinimumSearchPeakDetectorParameters"

    _fields = [
        "CHROMATOGRAPHIC_THRESHOLD_LEVEL",
        "SEARCH_RT_RANGE",
        "MIN_RELATIVE_HEIGHT",
        "MIN_ABSOLUTE_HEIGHT",
        "MIN_RATIO",
        "PEAK_DURATION",
    ]

    _time_in_minutes = ("PEAK_DURATION", "SEARCH_RT_RANGE")

    _defaults = {
        "chromatographic_threshold_level": 0.05,
        "search_rt_range": 0,
        "min_relative_height": 0.05,
        "min_absolute_height": 10,
        "min_ratio": 0.1,
        "peak_duration": (0, 5),
    }


class MinimumSearchPeakDetector(PeakResolver, _MinimumSearchPeakDetector):
    __doc__ = _MinimumSearchPeakDetector.__doc__


class IntensityWindowsSNParameters(metaclass=ParameterBaseMeta):

    _java_class = "IntensityWindowsSNParameters"


class WaveletCoefficientsSNParameters(metaclass=ParameterBaseMeta):

    _java_class = "WaveletCoefficientsSNParameters"

    _fields = ["HALF_WAVELET_WINDOW", "ABS_WAV_COEFFS"]


class _ADAPDetector(metaclass=ParameterBaseMeta):

    _java_class = "ADAPDetectorParameters"

    _fields = [
        "PEAK_DURATION",
        "RT_FOR_CWT_SCALES_DURATION",
        "SN_ESTIMATORS",
        "SN_THRESHOLD",
        "COEF_AREA_THRESHOLD",
        "MIN_FEAT_HEIGHT",
    ]
    _time_in_minutes = ("PEAK_DURATION", "RT_FOR_CWT_SCALES_DURATION")

    _module_combo_parameters = {
        "SN_ESTIMATORS": (IntensityWindowsSNParameters, WaveletCoefficientsSNParameters)
    }

    _defaults = {
        "rt_for_cwt_scales_duration": (0.1, 3),
        "coef_area_threshold": 100,
        "min_feat_height": 1000,
        "sn_threshold": 10,
    }


class ADAPDetector(PeakResolver, _ADAPDetector):
    __doc__ = _ADAPDetector.__doc__
